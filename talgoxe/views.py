# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from collections import OrderedDict
from re import match

from django import VERSION
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.db.models import Max
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, redirect
from django.template import loader, Context, RequestContext
from django.utils.datastructures import MultiValueDictKeyError

if VERSION[1] == 7 or VERSION[1] == 8:
    from django.core.urlresolvers import reverse
    from django.template import RequestContext
    from django.views.decorators.csrf import csrf_protect
else:
    from django.urls import reverse

from talgoxe.models import Spole, Artikel, Typ, Exporter, UnsupportedFormat

def render_template(request, template, context):
    if VERSION[1] == 7:
        return HttpResponse(template.render(RequestContext(request, context))) # Django version 1.7
    else:
        return HttpResponse(template.render(context, request)) # Django version 1.11

@login_required
def index(request):
    template = loader.get_template('talgoxe/index.html')
    artiklar = Artikel.objects.all()
    context = { 'artiklar' : artiklar, 'pagetitle' : "Talgoxe – Svenskt dialektlexikon", 'checkboxes' : False }
    return render_template(request, template, context)

@login_required # FIXME Något om användaren faktiskt är utloggad?
def create(request):
    nylemma = request.POST['nylemma'].strip()
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
    artikel = Artikel.objects.create(lemma = nylemma, rang = rang)
    return HttpResponseRedirect(reverse('redigera', args = (artikel.id,)))

@login_required
def redigera(request, id):
    method = request.META['REQUEST_METHOD']
    if method == 'POST':
        artikel = Artikel.objects.get(id = id)
        artikel.update(request.POST)

    template = loader.get_template('talgoxe/redigera.html')
    artiklar = Artikel.objects.all() # Anm. Svensk alfabetisk ordning verkar funka på frigg-test! Locale?
    artikel = Artikel.objects.get(id = id)
    artikel.collect()
    context = {
        'artikel': artikel,
        'artiklar': artiklar,
        'pagetitle': "%s – redigera i Svenskt dialektlexikon" % artikel.lemma,
    }

    return render_template(request, template, context)

@login_required
def artikel_efter_stickord(request, stickord):
    artiklar = Artikel.objects.filter(lemma = stickord)
    # TODO: 0!
    if len(artiklar) == 1:
        return HttpResponseRedirect(reverse('redigera', args = (artiklar.first().id,)))
    else:
        template = loader.get_template('talgoxe/stickord.html')
        context = {
            'artiklar' : artiklar
        }
        return render_template(request, template, context)

@login_required
def search(request): # TODO Fixa lista över artiklar när man POSTar efter omordning
    method = request.META['REQUEST_METHOD']
    if method == 'POST':
        ordning = []
        for artikel in request.POST:
            if match('^artikel-', artikel):
                id = artikel.replace('artikel-', '')
                ordning.append(Artikel.objects.get(id = id))
        föreArtikel = ordning[0]
        föreRang = 1
        for artikel in ordning[1:]:
            if artikel.lemma != föreArtikel.lemma and föreRang == 1:
                föreRang = 0
            if föreArtikel.rang != föreRang:
                föreArtikel.rang = föreRang
                föreArtikel.save()
            if artikel.lemma == föreArtikel.lemma:
                föreRang += 1
            else:
                föreRang = 1
            föreArtikel = artikel
    template = loader.get_template('talgoxe/search.html')
    uri = "%s://%s%s" % (request.scheme, request.META['HTTP_HOST'], request.path)
    if 'q' in request.GET:
        söksträng = request.GET['q']
    else:
        return render_template(request, template, { 'q' : 'NULL', 'uri' : uri })
    if 'sök-överallt' in request.GET and request.GET['sök-överallt'] != 'None':
        sök_överallt = request.GET['sök-överallt']
    else:
        sök_överallt = None
    if sök_överallt:
        sök_överallt_eller_inte = 'söker överallt'
    else:
        sök_överallt_eller_inte = 'söker bara uppslagsord'
    artiklar = list(Artikel.objects.filter(lemma__contains = söksträng))
    if sök_överallt:
        spolar = Spole.objects.filter(text__contains = söksträng).select_related('artikel')
        artiklar += [spole.artikel for spole in spolar]
    artiklar = sorted(list(OrderedDict.fromkeys(artiklar)), key = lambda artikel: (artikel.lemma, artikel.rang))
    context = {
            'q' : söksträng,
            'artiklar' : artiklar,
            'pagetitle' : '%d sökresultat för ”%s” (%s)' % (len(artiklar), söksträng, sök_överallt_eller_inte),
            'uri' : uri,
            'sök_överallt' : sök_överallt,
        }

    return render_template(request, template, context)

@login_required
def artikel(request, id):
    artikel = Artikel.objects.get(id = id)
    template = loader.get_template('talgoxe/artikel.html')
    artikel.collect()
    context = { 'artikel' : artikel, 'format' : format }

    return render_template(request, template, context)

@login_required
def print_on_demand(request):
    method = request.META['REQUEST_METHOD']
    template = loader.get_template('talgoxe/print_on_demand.html')
    if method == 'POST':
        artiklar = []
        for key in request.POST:
            mdata = match('selected-(\d+)', key)
            bdata = match('bokstav-(.)', key)
            if mdata:
                artiklar.append(Artikel.objects.get(id = int(mdata.group(1))))
            elif bdata:
                hel_bokstav = Artikel.objects.filter(lemma__startswith = bdata.group(1))
                artiklar += hel_bokstav
        artiklar = sorted(artiklar, key = lambda artikel: (artikel.lemma, artikel.rang)) # TODO Make unique
        context = { 'artiklar' : artiklar, 'redo' : True, 'titel' : 'Ditt urval på %d artiklar' % len(artiklar), 'pagetitle' : '%d artiklar' % len(artiklar) }
        template = loader.get_template('talgoxe/search.html')
    elif method == 'GET':
        artiklar = Artikel.objects.order_by('lemma', 'rang')
        bokstäver = [chr(i) for i in range(0x61, 0x7B)] + ['å', 'ä', 'ö']
        context = { 'artiklar' : artiklar, 'checkboxes' : True, 'bokstäver' : bokstäver, 'pagetitle' : '%d artiklar' % artiklar.count() }

    return render_template(request, template, context)

@login_required
def print(request, format):
    if format not in ['pdf', 'odt', 'docx']:
        raise UnsupportedFormat(format)
    template = loader.get_template('talgoxe/download_document.html')
    exporter = Exporter(format)
    exporter.export_letters()
    filepath = exporter.export(list(map(lambda s: s.strip(), request.GET['ids'].split(','))))
    context = { 'filepath' : filepath }

    return render_template(request, template, context)

def easylogout(request):
    logout(request)
    template = loader.get_template("talgoxe/logout.html")
    return render_template(request, template, { })
