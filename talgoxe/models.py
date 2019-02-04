# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import datetime
from django.core.exceptions import ObjectDoesNotExist
from django.db import models
from django.db.models import Max
from math import floor
from re import match, split
from talgoxe.Province import Province


class UnsupportedFormat(Exception):
  pass


class Artikel(models.Model):
    class Meta:
        ordering = ('lemma_sortable', 'rang')

    lemma = models.CharField(max_length = 100)
    lemma_sortable = models.CharField(max_length = 100)
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

    @staticmethod
    def create(post_data):
        nylemma = post_data['stickord']
        företrädare = Artikel.objects.filter(lemma = nylemma)
        maxrang = företrädare.aggregate(Max('rang'))['rang__max']
        if maxrang == None:
            rang = 0
        elif maxrang == 0:
            artikel0 = företrädare.first()
            artikel0.rang = 1
            artikel0.save()
            rang = 2
        elif maxrang > 0:
            rang = maxrang + 1
        article = Artikel.objects.create(lemma = nylemma, lemma_sortable = Artikel.get_lemma_sortable(nylemma), rang = rang)
        article.update(post_data)
        return article

    def get_spole(self, i):
        if i < len(self.spolar()):
            return self.spolar()[i] # Man kan missa vissa värden av pos, så .get(pos = i) funkar inte. Se t.ex. 1öden (id 3012683), spole saknas för pos = 2. AR 2018-06-03.
        else:
            return None

    @staticmethod
    def get_lemma_sortable(lemma):
        lemma_sortable = lemma.lower()
        lemma_sortable = lemma_sortable.replace('Å', 'å')
        lemma_sortable = lemma_sortable.replace('Ä', 'ä')
        lemma_sortable = lemma_sortable.replace('Ö', 'ö')
        lemma_sortable = lemma_sortable.replace('?', '')
        lemma_sortable = lemma_sortable.replace(',', '')
        lemma_sortable = lemma_sortable.replace('(', '')
        lemma_sortable = lemma_sortable.replace(')', '')
        lemma_sortable = lemma_sortable.replace('-', '')
        return lemma_sortable

    def spolar(self):
        if not hasattr(self, 'spolarna'):
            allSpolar = self.spole_set.all();
            if len(allSpolar) == 0: # Artikeln skapades just, vi fejkar en första spole
                ok = Typ.objects.get(kod = 'OK')
                spole = Spole(typ = ok, text = '', pos = 0)
                self.spolarna = [spole]
            else:
                self.spolarna = allSpolar

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
            huvudtyp = spole.getType()
            for bit in bits:
                if bits.index(bit) > 0:
                    i += 1
                    if i < len(self.spolar()):
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
        sorted_landskap = sorted(self.landskap, key = Province.key)
        if len(sorted_landskap) > 1:
            # Remove province duplicates.
            index = 0;
            while index < (len(sorted_landskap) - 1):
                if sorted_landskap[index].abbreviation == sorted_landskap[index + 1].abbreviation:
                    del sorted_landskap[index]
                else:
                    index += 1
        sorted_landskap = Province.reduce_provinces(sorted_landskap)
        for ls in sorted_landskap:
           fjäder = Fjäder(ArticleTypeManager.get_type_by_abbreviation('g'), ls.abbreviation)
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
            if spole.isgeo() and spole.text == "":
                i += 1
                continue
            if state == 'ALLMÄNT':
                if spole.isgeo():
                    self.landskap = [Province(spole.text)]
                    state = 'GEOGRAFI'
                else:
                    i = self.analyse_spole(i)
                    self.preventnextspace = spole.isleftdelim()
                    # state är fortfarande 'ALLMÄNT'
            elif state == 'GEOGRAFI':
                if spole.isgeo():
                    self.landskap.append(Province(spole.text))
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

    def collect2(self, spolar):
        self.spolarna = spolar
        self.collect()

    def update(self, post_data):
        order = post_data['order'].split(',')
        stickord = post_data['stickord']
        self.uppdaterat = datetime.datetime.now()
        if self.lemma != stickord:
            self.lemma = stickord
            self.lemma_sortable = Artikel.get_lemma_sortable(stickord)
            self.save()
        d = [[post_data['type-' + key].strip(), post_data['value-' + key].strip()] for key in order]
        gtype = Typ.objects.get(kod='g')
        for i in range(len(d)):
            bit = d[i]
            try:
                type = Typ.objects.get(kod=bit[0])
            except ObjectDoesNotExist:  # FIXME Do something useful!
                # TODO >>> Type.objects.create(abbreviation = 'OG', name = 'Ogiltig', id = 63)
                type = Typ.objects.get(kod='OG')
            text = bit[1]
            if type == gtype and text.title() in Province.province_abbreviation.keys():
                text = Province.province_abbreviation[text.title()]
            data = self.get_spole(i)
            if data and (data.artikel_id != None):
                data.pos = i
                data.typ = type
                data.text = text
                data.save()
            else:
                Spole.objects.create(artikel=self, typ=type, pos=i, text=text)
        self.spole_set.filter(pos__gte=len(d)).delete()


    @staticmethod
    def update_lemma_sortable():
        articles = Artikel.objects.all()
        for article in articles:
            article.lemma_sortable = Artikel.get_lemma_sortable(article.lemma)
            article.save()


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


article_types_by_abbreviation = {}
article_types_by_id = {}


class ArticleTypeManager:

    @staticmethod
    def get_type_by_abbreviation(abbreviation):
        ArticleTypeManager.init_types()

        # Get requested article type.
        if abbreviation in article_types_by_abbreviation:
            return article_types_by_abbreviation[abbreviation]
        else:
            raise ObjectDoesNotExist("No article type with abbreviation = " + abbreviation)

    @staticmethod
    def get_type_by_id(id):
        ArticleTypeManager.init_types()

        # Get requested article type.
        if id in article_types_by_id:
            return article_types_by_id[id]
        else:
            raise ObjectDoesNotExist("No article type with id = " + str(id))

    @staticmethod
    def init_types():
        if len(article_types_by_id) == 0:
            # Get all article types.
            allArticleTypes = Typ.objects.all()
            for articleType in allArticleTypes:
                article_types_by_abbreviation[articleType.kod] = articleType
                article_types_by_id[articleType.id] = articleType


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
        return self.getType().__str__() + ' ' + self.text

    def webstyle(self):
        self.webstyles[self.getType().__str__()]

    def printstyle(self):
        self.printstyles[self.getType().__str__()]

    def isgeo(self):
        return self.getType().isgeo()
        # return self.typ.isgeo()

    def isleftdelim(self):
        return self.getType().kod.upper() in ['VR', 'VH']

    def getType(self):
        return ArticleTypeManager.get_type_by_id(self.typ_id)


class Fjäder:
    def __init__(self, spole, text = None):
        self.display = None # FIXME Måste inte ändras för KO
        if text: # spole är egentligen en Typ
            self.typ = spole.kod.upper()
            self.text = text.strip()
        else:
            self.typ = spole.getType().kod.upper()
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

