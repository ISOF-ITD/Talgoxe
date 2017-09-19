# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import re
from tempfile import mkdtemp

from django.db import models

# Create your models here.

# Not using migration; instead dump the SQL, remove the AUTO_INCREMENT FROM primary keys,
# and copy the existing table into them.  For Data (table fdata), this is needed:
# INSERT INTO talgoxe_data (id, d, pos, lemma_id, type_id) SELECT d_id, d, pos, l_id, typ FROM fdata WHERE typ IN (SELECT nr FROM typer) AND l_id IN (SELECT l_id FROM lemma);
# Foreign keys fails otherwise!
class Lemma(models.Model):
    lemma = models.CharField(max_length = 100)
    segments = []

    def __str__(self):
        return self.lemma

    def __unicode__(self):
        return self.lemma

    def raw_data_set(self):
        return self.data_set.filter(id__gt = 0).order_by('pos')

    def resolve_pilcrow(self):
        i = 0
        currmoment1 = []
        currmoment2 = []
        self.segments = []
        state = 'INITIAL'
        gtype = None
        while i < self.raw_data_set().count():
            currseg = self.raw_data_set().all()[i]
            if state == 'GEOGRAFI':
                if currseg.type.__unicode__() == u'G':
                    landskap.append(Landskap(currseg.d))
                else: # Sort and flush
                    sorted_landskap = sorted(landskap, Landskap.cmp)
                    landskap = []
                    for ls in sorted_landskap:
                        currmoment2.append(Segment(gtype, ls.abbrev))
                    currmoment2.append(Segment(currseg.type, currseg.d))
                    state = 'INITIAL'
            else:
                if currseg.type.__unicode__() == u'M1':
                    currmoment1.append(currmoment2)
                    self.segments.append(currmoment1)
                    currmoment1 = []
                    currmoment2 = []
                elif currseg.type.__unicode__() == u'M2':
                    currmoment1.append(currmoment2)
                    currmoment2 = []
                elif currseg.type.__unicode__() == u'G':
                    gtype = currseg.type
                    state = 'GEOGRAFI'
                    landskap = [Landskap(currseg.d)]
                elif currseg.type.__unicode__() == u'VH':
                    currmoment2.append(Segment(currseg.type, '['))
                elif currseg.type.__unicode__() == u'HH':
                    currmoment2.append(Segment(currseg.type, ']'))
                elif currseg.type.__unicode__() == u'VR':
                    currmoment2.append(Segment(currseg.type, '('))
                elif currseg.type.__unicode__() == u'HR':
                    currmoment2.append(Segment(currseg.type, ')'))
                else:
                    subsegs = re.split(ur'¶', currseg.d)
                    if len(subsegs) == 1:
                        currmoment2.append(Segment(currseg.type, subsegs[0]))
                    else:
                        maintype = currseg.type
                        currmoment2.append(Segment(maintype, subsegs[0]))
                        for j in range(1, len(subsegs)):
                            i += 1
                            subseg = self.raw_data_set().all()[i]
                            currmoment2.append(Segment(subseg.type, subseg.d))
                            currmoment2.append(Segment(maintype, subsegs[j]))
            i += 1
        currmoment1.append(currmoment2)
        self.segments.append(currmoment1)

    def collect(self):
        self.new_segments = []
        i = 0
        while i < self.raw_data_set().count():
            currseg = self.raw_data_set().all()[i]
            bits = re.split(ur'¶', currseg.d)
            if len(bits) == 1:
                self.new_segments.append(currseg)
            else:
                maintype = currseg.type
                self.new_segments.append(Segment(maintype, bits[0]))
                print(i)
                for bit in bits:
                    print(bit)
                    print(bits.index(bit))
                    if bits.index(bit) > 0:
                        i += 1
                        self.new_segments.append(self.raw_data_set().all()[i])
                    self.new_segments.append(Segment(maintype, bit))
            i += 1

    def process(self, outfile):
        self.resolve_pilcrow()
        outfile.write(('\\hskip-1em\\SDL:SO{%s} ' % self.lemma).encode('UTF-8'))
        prevseg = self.segments[0][0][0]
        for m1 in range(len(self.segments)):
            moment1 = self.segments[m1]
            if m1 > 0 and len(self.segments) > 1:
                sec = Segment('M1', '%d' % m1)
                if prevseg:
                    prevseg.output(outfile, sec)
                prevseg = sec
            for m2 in range(len(moment1)):
                moment2 = moment1[m2]
                if m2 > 0 and len(moment1) > 1:
                    outfile.write('\SDL:M2{%c} ' % (96 + m2))
                    sec = Segment('M2', '%c' % (96 + m2))
                    if prevseg:
                        prevseg.output(outfile, sec)
                    prevseg = sec
                for seg in moment2:
                    if prevseg:
                        prevseg.output(outfile, seg)
                    prevseg = seg
                prevseg.output(outfile, prevseg) # FIXME Remove potential final space
        outfile.write("\n")

class Segment():
    def __init__(self, type, text):
        self.type = type
        self.text = text

    def __str__(self):
        return self.type.__str__() + ' ' + self.text

    def __unicode__(self):
        return self.type.__unicode__() + ' ' + self.text

    def isrightdelim(self):
        return self.type.__unicode__() == 'HH' or self.type.__unicode__() == 'HR' or self.type.__unicode__() == 'IP'

    def output(self, outfile, next):
        outfile.write(('\SDL:%s{' % self.type.__unicode__()).encode('UTF-8'))
        outfile.write(self.text.replace(u'\\', '\\backslash ').encode('UTF-8'))
        outfile.write('}')
        if not next.isrightdelim():
            outfile.write(' ')

    # TODO Method hyphornot()

class Type(models.Model):
    abbrev = models.CharField(max_length = 5)
    name = models.CharField(max_length = 30)

    def __str__(self):
        return self.abbrev.upper()

    def __unicode__(self):
        return self.abbrev.upper()

    def format(self):
        out = self.__unicode__()
        out += (4 - len(out)) * '\xa0'
        return out

class Data(models.Model):
    d = models.CharField(max_length = 2000)
    pos = models.SmallIntegerField()
    lemma = models.ForeignKey(Lemma)
    type = models.ForeignKey(Type)

    def __str__(self):
        return self.type.__str__() + ' ' + self.d

    def __unicode__(self):
        return self.type.__unicode__() + ' ' + self.d

    def webstyle(self):
        self.webstyles[self.type.__unicode__()]

    def printstyle(self):
        self.printstyles[self.type.__unicode__()]

    def format(self):
        return d.strip()

class Landskap():
    ordning = [
        u'Skåne', u'Blek', u'Öland', u'Smål', u'Hall', u'Västg', u'Boh', u'Dalsl', u'Gotl', u'Östg', # 0-9
        u'Götal', # 10
        u'Sörml', u'Närke', u'Värml', u'Uppl', u'Västm', u'Dal', # 11 - 16
        u'Sveal', # 17
        u'Gästr', u'Häls', u'Härj', u'Med', u'Jämtl', u'Ång', u'Västb', u'Lappl', u'Norrb', # 18 - 26
        u'Norrl', # 27
    ]

    def cmp(self, other):
        if self.abbrev in self.ordning and other.abbrev in self.ordning:
            return cmp(self.ordning.index(self.abbrev), self.ordning.index(other.abbrev))
        else:
            return 0

    def __init__(self, abbrev):
        self.abbrev = abbrev.capitalize()

    def __str__(self):
        return self.abbrev

    def __unicode__(self):
        return self.abbrev

class Lexicon():
    def process(self):
        tempdir = mkdtemp('', 'SDL')
        source = file(tempdir + '/sdl.tex', 'w')
        source.write("""
            \starttext
            {\\tfc\\hfill Sveriges dialektlexikon\\hfill}

            {\\tfb\\hfill utgiven av Institutet för språk och folkminnen\\hfill}
        """.encode('UTF-8'))
        for lemma in Lemma.objects.filter(id__gt = 0).order_by('lemma'):
            print(lemma.lemma)
            lemma.process(source)
        source.close()
