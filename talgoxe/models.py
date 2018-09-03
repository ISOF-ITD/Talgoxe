# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from math import floor
from os import chdir, popen, rename, environ
from os.path import abspath, dirname, join
from re import match, split
from tempfile import mkdtemp, mktemp

import ezodf
import docx

from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from django.db import models

# FIXME Superscripts!

class UnsupportedFormat(Exception):
  pass

class Artikel(models.Model):
    class Meta:
        ordering = ('lemma', 'rang')

    lemma = models.CharField(max_length = 100)
    rang = models.SmallIntegerField()
    skapat = models.DateTimeField(auto_now_add = True)
    uppdaterat = models.DateTimeField(auto_now = True)
    segments = []

    superscripts = [
        '⁰', '¹', '²', '³', '⁴', '⁵', '⁶', '⁷', '⁸', '⁹',
    ]

    def __str__(self):
        r = self.rang
        prefix = ''
        while r > 0:
            prefix = Artikel.superscripts[r % 10] + prefix
            r = floor(r / 10)
        return prefix + self.lemma

    def get_spole(self, i):
        if i < len(self.spolar()):
            return self.spolar()[i] # Man kan missa vissa värden av pos, så .get(pos = i) funkar inte. Se t.ex. 1öden (id 3012683), spole saknas för pos = 2. AR 2018-06-03.
        else:
            return None

    def spolar(self):
        if not hasattr(self, 'spolarna'):
            if self.spole_set.count() == 0: # Artikeln skapades just, vi fejkar en första spole
                ok = Typ.objects.get(kod = 'OK')
                spole = Spole(typ = ok, text = '', pos = 0)
                self.spolarna = [spole]
            else:
                self.spolarna = self.spole_set.all()

        return self.spolarna

    def number_moments(self, type):
        if type == 'M1':
            format = '%d'
            offset = 1
        elif type == 'M2':
            format = '%c'
            offset = 97
        if len(self.moments[type]) > 1:
            for m in range(len(self.moments[type])):
                self.moments[type][m].text = format % (m + offset)
                self.moments[type][m].display = True

    def analyse_spole(self, i):
        spole = self.get_spole(i)
        bits = split(u'¶', spole.text)
        if len(bits) == 1:
            self.append_fjäder(spole)
        else:
            huvudtyp = spole.typ
            for bit in bits:
                if bits.index(bit) > 0:
                    i += 1
                    self.append_fjäder(Fjäder(self.get_spole(i)), True)
                if bit:
                    fjäder = Fjäder(huvudtyp, bit)
                    if self.preventnextspace and bits.index(bit) == 0:
                        fjäder.preventspace = True
                    self.append_fjäder(fjäder, True)
        return i

    def append_fjäder(self, data, skipmoments = False):
        if skipmoments:
            segment = data
        else:
            segment = Fjäder(data)
            segment.preventspace = self.preventnextspace
            if segment.ism1():
                self.number_moments('M2')
                self.moments['M2'] = []
                self.moments['M1'].append(segment)
            elif segment.ism2():
                self.moments['M2'].append(segment)
        self.fjädrar.append(segment)

    def flush_landskap(self):
        sorted_landskap = sorted(self.landskap, key = Landskap.key)
        print(list(map(lambda l: l.abbrev, sorted_landskap)))
        for ls in sorted_landskap:
           fjäder = Fjäder(Typ.objects.get(kod = 'g'), ls.abbrev)
           if self.preventnextspace and sorted_landskap.index(ls) == 0:
               fjäder.preventspace = True
           self.append_fjäder(fjäder, True)
        self.landskap = []

    def collect(self):
        self.fjädrar = []
        self.preventnextspace = False
        i = 0
        state = 'ALLMÄNT'
        self.moments = { 'M1': [], 'M2': [] }
        self.landskap = []
        while i < len(self.spolar()):
            spole = self.get_spole(i)
            if state == 'ALLMÄNT':
                if spole.isgeo():
                    self.landskap = [Landskap(spole.text)]
                    state = 'GEOGRAFI'
                else:
                    i = self.analyse_spole(i)
                    self.preventnextspace = spole.isleftdelim()
                    # state är fortfarande 'ALLMÄNT'
            elif state == 'GEOGRAFI':
                if spole.isgeo():
                    self.landskap.append(Landskap(spole.text))
                    # state är fortfarande 'GEOGRAFI'
                else:
                    self.flush_landskap()
                    i = self.analyse_spole(i) # För pilcrow i ”hårgård” och ”häringa”
                    self.preventnextspace = spole.isleftdelim()
                    state = 'ALLMÄNT'
            i += 1
        if self.landskap: # För landskapsnamnet på slutet av ”häringa”, efter bugfixet ovan
            self.flush_landskap()
        self.number_moments('M1')
        self.number_moments('M2')
        self.moments = { 'M1': [], 'M2': [] }

    def update(self, post_data):
        order = post_data['order'].split(',')
        stickord = post_data['stickord']
        if self.lemma != stickord:
            self.lemma = stickord
            self.save()
        d = [[post_data['type-' + key].strip(), post_data['value-' + key].strip()] for key in order]
        gtype = Typ.objects.get(kod = 'g')
        for i in range(len(d)):
            bit = d[i]
            try:
                type = Typ.objects.get(kod = bit[0])
            except ObjectDoesNotExist: # FIXME Do something useful!
# TODO >>> Type.objects.create(abbrev = 'OG', name = 'Ogiltig', id = 63)
                type = Typ.objects.get(kod = 'OG')
            text = bit[1]
            if type == gtype and text.title() in Landskap.short_abbrev.keys():
              text = Landskap.short_abbrev[text.title()]
            data = self.get_spole(i)
            if data:
                data.typ = type
                data.text = text
                data.save()
            else:
                Spole.objects.create(artikel = self, typ = type, pos = i, text = text)
        self.spole_set.filter(pos__gte = len(d)).delete()

class Segment(): # Fjäder!
    def __init__(self, type, text = None):
        self.display = None
        if text != None:
            self.type = type
            self.text = text
        else: # type is actually a Data object
            self.type = type.typ
            self.text = type.text

    def __str__(self):
        return self.type.__str__() + ' ' + self.text

    def isgeo(self):
        return self.type.isgeo()

    def isleftdelim(self):
        if type(self.type) == 'unicode':
            return self.type in ['vh', 'vr']
        else:
            return self.type.isleftdelim()

    def isrightdelim(self):
        if type(self.type) == 'unicode' or str(type(self.type)) == "<type 'unicode'>":
            return self.type in ['hh', 'hr', 'ip', 'ko'] # KO is convenient
        else:
            return self.type.isrightdelim()

    def ismoment(self):
        return self.ism1() or self.ism2()

    def ism1(self):
        return self.type.ism1()

    def ism2(self):
        return self.type.ism2()

    def output(self, outfile, next):
        outfile.write(('\SDL:%s{' % self.type).encode('UTF-8'))
        outfile.write(self.text.replace(u'\\', '\\backslash ').encode('UTF-8'))
        outfile.write('}')
        if not next.isrightdelim():
            outfile.write(' ')

    # TODO Method hyphornot()

    def format(self):
        if self.type.__str__().upper() == 'VH':
            return '['
        elif self.type.__str__().upper() == 'HH':
            return ']'
        elif self.type.__str__().upper() == 'VR':
            return '('
        elif self.type.__str__().upper() == 'HR':
            return ')'
        elif self.type.__str__().upper() == 'ÄV':
            return 'äv.'
        else:
            return self.text.strip()

class Typ(models.Model):
    kod = models.CharField(max_length = 5)
    namn = models.CharField(max_length = 30)
    skapat = models.DateTimeField(auto_now_add = True)
    uppdaterat = models.DateTimeField(auto_now = True)

    def __str__(self):
        return self.kod.upper()

    def isgeo(self):
        return self.kod == 'g'

    def format(self):
        out = self.__str__()
        out += (4 - len(out)) * '\xa0'
        return out

class Spole(models.Model):
    text = models.CharField(max_length = 2000)
    pos = models.SmallIntegerField()
    artikel = models.ForeignKey(Artikel)
    typ = models.ForeignKey(Typ)
    skapat = models.DateTimeField(auto_now_add = True)
    uppdaterat = models.DateTimeField(auto_now = True)

    class Meta:
        ordering = ('pos',)

    def __str__(self):
        return self.typ.__str__() + ' ' + self.text

    def webstyle(self):
        self.webstyles[self.typ.__str__()]

    def printstyle(self):
        self.printstyles[self.typ.__str__()]

    def isgeo(self):
        return self.typ.isgeo()

    def isleftdelim(self):
        return self.typ.kod.upper() in ['VR', 'VH']

class Fjäder:
    def __init__(self, spole, text = None):
        self.display = None # FIXME Måste inte ändras för KO
        if text: # spole är egentligen en Typ
            self.typ = spole.kod.upper()
            self.text = text.strip()
        else:
            self.typ = spole.typ.kod.upper()
            self.text = spole.text.strip()
        self.preventspace = False

    def isrightdelim(self):
        return self.typ in ['HH', 'HR', 'IP', 'KO'] or match(r'^,', self.text)

    def ismoment(self):
        return self.ism1() or self.ism2()

    def ism1(self):
        return self.typ == 'M1'

    def ism2(self):
        return self.typ == 'M2'

    def format(self): # FIXME Också för P:er från ÖVP?
        if self.typ == 'VR':
            return '('
        elif self.typ == 'HR':
            return ')'
        elif self.typ == 'VH':
            return '['
        elif self.typ == 'HH':
            return ']'
        elif self.typ == 'ÄV':
            return 'äv.'
        else:
            return self.text

    def type(self): # FIXME Remove later!
        return self.typ

    def setspace(self):
        return not self.preventspace and not self.isrightdelim() # TODO Lägga till det med den föregående fjädern

class Landskap():
    ordning = [
        u'Skåne', u'Blek', u'Öland', u'Smål', u'Hall', u'Västg', u'Boh', u'Dalsl', u'Gotl', u'Östg', # 0-9
        u'Götal', # 10
        u'Sörml', u'Närke', u'Värml', u'Uppl', u'Västm', u'Dal', # 11 - 16
        u'Sveal', # 17
        u'Gästr', u'Häls', u'Härj', u'Med', u'Jämtl', u'Ång', u'Västb', u'Lappl', u'Norrb', # 18 - 26
        u'Norrl', # 27
    ]

    # TODO: Something more object-oriented (methods short, long, rank)
    short_abbrev = {
      u'Sk' : u'Skåne',
      u'Bl' : u'Blek',
      u'Öl' : u'Öland',
      u'Sm' : u'Smål',
      u'Ha' : u'Hall',
      u'Vg' : u'Västg',
      u'Bo' : u'Boh',
      u'Dsl': u'Dalsl',
      u'Gl' : u'Gotl',
      u'Ög' : u'Östg',
      u'Götal' : u'Götal',
      u'Sdm': u'Sörml',
      u'Nk' : u'Närke',
      u'Vrm': u'Värml',
      u'Ul' : u'Uppl',
      u'Vstm' : u'Västm',
      u'Dal': u'Dal',
      u'Sveal' : u'Sveal',
      u'Gst': u'Gästr',
      u'Hsl': u'Häls',
      u'Hrj': u'Härj',
      u'Mp' : u'Med',
      u'Jl' : u'Jämtl',
      u'Åm' : u'Ång',
      u'Vb' : u'Västb',
      u'Lpl': u'Lappl',
      u'Nb' : u'Norrb',
      u'Norrl' : u'Norrl',
    }

    def cmp(self, other):
        if self.abbrev in self.ordning and other.abbrev in self.ordning:
            return cmp(self.ordning.index(self.abbrev), self.ordning.index(other.abbrev))
        else:
            return 0

    @staticmethod
    def key(self):
        if self.abbrev in self.ordning:
            return self.ordning.index(self.abbrev)
        else:
            return -1 # Så det är lättare att se dem

    def __init__(self, abbrev):
        self.abbrev = abbrev.capitalize()

    def __str__(self):
        return self.abbrev

    @staticmethod
    def reduce_landskap(lista):
        antal_per_del = { 'Götal' : 7, 'Sveal' : 4, 'Norrl' : 6 }
        delar = ['Götal', 'Sveal', 'Norrl']
        landskap_per_del = { 'Götal' : [], 'Sveal' : [], 'Norrl' : [] }
        for landskap in lista:
            if Landskap.ordning.index(landskap.abbrev) < Landskap.ordning.index('Götal'):
                landskap_per_del['Götal'].append(landskap)
            elif Landskap.ordning.index(landskap.abbrev) < Landskap.ordning.index('Sveal'):
                landskap_per_del['Sveal'].append(landskap)
            else:
                landskap_per_del['Norrl'].append(landskap)
            print(landskap)
        print(len(landskap_per_del['Götal']))
        utskriftsform = []
        for landsdel, landskapen in landskap_per_del.items():
            if len(landskapen) >= antal_per_del[landsdel]:
                utskriftsform.append(Landskap(landsdel))
            else:
                utskriftsform += sorted(landskapen, key = Landskap.key)

        return utskriftsform

class Exporter:
    def __init__(self, format):
        self.format = format
        initialisers = {
            'pdf' : self.start_pdf,
            'odt' : self.start_odf,
            'docx' : self.start_docx,
        }

        generators = {
            'pdf' : self.generate_pdf_paragraph,
            'odt' : self.generate_odf_paragraph,
            'docx' : self.generate_docx_paragraph,
        }

        savers = {
            'pdf' : self.save_pdf,
            'odt' : self.save_odf,
            'docx' : self.save_docx,
        }

        self.start_document = initialisers[format]
        self.generate_paragraph = generators[format]
        self.save_document = savers[format]

    def generate_pdf_paragraph(self, artikel):
        self.document.write("\\hskip-0.5em")
        if artikel.rang > 0:
            self.document.write('\lohi[left]{}{\SDL:SO{%d}}' % artikel.rang) # TODO Real superscript
        self.document.write("\\SDL:SO{%s}" % artikel.lemma)
        for segment in artikel.fjädrar: # TODO Handle moments!  segment.ismoment and segment.display
            if not segment.preventspace and not segment.isrightdelim():
                self.document.write(' ') # FIXME But not if previous segment is left delim!
            type = segment.typ
            text = segment.format().replace(u'\\', '\\textbackslash ').replace('~', '{\\char"7E}')
            self.document.write(('\\SDL:%s{%s}' % (type, text)))
        self.document.write("\\par")

    def start_pdf(self):
        self.document = open(self.filename.replace('.pdf', '.tex'), 'w')
        self.document.write("\\mainlanguage[sv]")
        self.document.write("\\setupbodyfont[pagella, 12pt]\n")
        self.document.write("\\setuppagenumbering[state=stop]\n")
        with open(join(dirname(abspath(__file__)), 'lib', 'sdl-setup.tex'), 'r', encoding = 'UTF-8') as file:
            self.document.write(file.read())

        self.document.write("""
            \\starttext
            """)

        self.document.write("\\startcolumns[n=2,balance=yes]\n")

    def save_pdf(self):
        self.document.write("\\stopcolumns\n")
        self.document.write("\\stoptext\n")
        self.document.close()

        chdir(self.dirname)
        environ['PATH'] = "%s:%s" % (settings.CONTEXT_PATH, environ['PATH'])
        environ['TMPDIR'] = '/tmp'
        popen("context --batchmode sdl.tex").read()

    def add_odf_style(self, type, xmlchunk):
        self.document.inject_style("""
            <style:style style:name="%s" style:family="text">
                <style:text-properties %s />
            </style:style>
            """ % (type, xmlchunk))

    def start_odf(self):
        self.document = ezodf.newdoc(doctype = 'odt', filename = self.filename)
        self.add_odf_style('SO', 'fo:font-weight="bold"')
        self.add_odf_style('OK', 'fo:font-size="9pt"')
        self.add_odf_style('G', 'fo:font-size="9pt"')
        self.add_odf_style('DSP', 'fo:font-style="italic"')
        self.add_odf_style('TIP', 'fo:font-size="9pt"')
        # IP
        self.add_odf_style('M1', 'fo:font-weight="bold"')
        self.add_odf_style('M2', 'fo:font-weight="bold"')
        # VH, HH, VR, HR
        self.add_odf_style('REF', 'fo:font-weight="bold"')
        self.add_odf_style('FO', 'fo:font-style="italic"')
        self.add_odf_style('TIK', 'fo:font-style="italic" fo:font-size="9pt"')
        self.add_odf_style('FLV', 'fo:font-weight="bold" fo:font-size="9pt"')
        # ÖVP. Se nedan!
        # BE, ÖV
        # ÄV, ÄVK se nedan
        # FOT
        self.add_odf_style('GT', 'fo:font-size="9pt"')
        self.add_odf_style('SOV', 'fo:font-weight="bold"')
        # TI
        # HV, INT
        self.add_odf_style('OKT', 'fo:font-size="9pt"')
        # VS
        self.add_odf_style('GÖ', 'fo:font-size="9pt"')
        # GP, UST
        self.add_odf_style('US', 'fo:font-style="italic"')
        # GÖP, GTP, NYR, VB
        self.add_odf_style('OG', 'style:text-line-through-style="solid"')
        self.add_odf_style('SP', 'fo:font-style="italic"')

    def save_odf(self):
        self.document.save()

    def generate_odf_paragraph(self, artikel):
        paragraph = ezodf.Paragraph()
        paragraph += ezodf.Span(artikel.lemma, style_name = 'SO') # TODO Homografnumrering!
        for segment in artikel.fjädrar:
            type = segment.typ
            if not type == 'KO':
                if not segment.preventspace and not segment.isrightdelim():
                    paragraph += ezodf.Span(' ')
                paragraph += ezodf.Span(segment.format(), style_name = type)
        self.document.body += paragraph

    def start_docx(self):
        self.document = docx.Document()
        self.add_docx_styles()
        return self.document

    def save_docx(self):
        self.document.save(self.filename)

    def generate_docx_paragraph(self, artikel):
        paragraph = self.document.add_paragraph()
        if artikel.rang > 0:
            paragraph.add_run(str(artikel.rang), style = 'SO').font.superscript = True
        paragraph.add_run(artikel.lemma, style = 'SO')
        for segment in artikel.fjädrar:
            type = segment.typ
            if not type == 'KO':
                if not segment.preventspace and not segment.isrightdelim():
                    paragraph.add_run(' ', style = self.document.styles[type])
                if type == 'ÖVP': # TODO Något bättre
                    run = '(' + segment.format() + ')'
                else:
                    run = segment.format()
                paragraph.add_run(run, style = self.document.styles[type])

    def add_docx_styles(self): # TODO Keyword arguments?
        self.add_docx_style('SO', False, True, 12)
        self.add_docx_style('OK', False, False, 9)
        self.add_docx_style('G', False, False, 9)
        self.add_docx_style('DSP', True, False, 12)
        self.add_docx_style('TIP', False, False, 9)
        self.add_docx_style('IP', False, False, 12)
        self.add_docx_style('M1', False, True, 12)
        self.add_docx_style('M2', False, True, 12)
        self.add_docx_style('VH', False, False, 12)
        self.add_docx_style('HH', False, False, 12)
        self.add_docx_style('VR', False, False, 12)
        self.add_docx_style('HR', False, False, 12)
        self.add_docx_style('REF', False, True, 12)
        self.add_docx_style('FO', True, False, 12)
        self.add_docx_style('TIK', True, False, 9)
        self.add_docx_style('FLV', False, True, 9)
        self.add_docx_style('ÖVP', False, False, 12)
        self.add_docx_style('BE', False, False, 12)
        self.add_docx_style('ÖV', False, False, 12)
        self.add_docx_style('ÄV', False, False, 12) # FIXME Skriv “även” :-)
        self.add_docx_style('ÄVK', True, False, 12) # FIXME Skriv även även här ;-)
        self.add_docx_style('FOT', True, False, 12)
        self.add_docx_style('GT', False, False, 9)
        self.add_docx_style('SOV', False, True, 12)
        for style in ('TI', 'HV', 'INT'):
            self.add_docx_style(style)
        self.add_docx_style('OKT', False, False, 9)
        self.add_docx_style('VS')
        self.add_docx_style('GÖ', False, False, 9)
        self.add_docx_style('GP')
        self.add_docx_style('UST', True, False, 12)
        self.add_docx_style('US', True, False, 12)
        for style in ('GÖP', 'GTP', 'NYR', 'VB'):
            self.add_docx_style(style)
        OG = self.document.styles.add_style('OG', docx.enum.style.WD_STYLE_TYPE.CHARACTER)
        OG.font.strike = True
        self.add_docx_style('SP', True, False, 12)
        self.add_docx_style('M0', False, True, 18)
        self.add_docx_style('M3', True, False, 6)

    def add_docx_style(self, type, italic = False, bold = False, size = 12):
        style = self.document.styles.add_style(type, docx.enum.style.WD_STYLE_TYPE.CHARACTER)
        style.base_style = self.document.styles['Default Paragraph Font']
        if italic:
            style.font.italic = True
        if bold:
            style.font.bold = True
        style.font.size = docx.shared.Pt(size)

    def export(self, ids):
        self.dirname = mkdtemp('', 'SDLartikel')
        self.filename = join(self.dirname, 'sdl.%s' % self.format)
        self.start_document()
        if len(ids) == 1:
            artikel = Artikel.objects.get(id = ids[0])
            artikel.collect()
            self.generate_paragraph(artikel)
            filename = '%s-%s.%s' % (ids[0], artikel.lemma, self.format)
        else:
            filename = 'sdl-utdrag.%s' % self.format # FIXME Unikt namn osv.
            for id in ids:
                artikel = Artikel.objects.get(id = id)
                artikel.collect()
                self.generate_paragraph(artikel)
        self.save_document()
        staticpath = join(dirname(abspath(__file__)), 'static', 'ord')
        rename(self.filename, join(staticpath, filename))

        return join('ord', filename)
