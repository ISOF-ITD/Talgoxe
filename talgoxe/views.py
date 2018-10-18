# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from collections import OrderedDict
from re import match

from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.db.models import Max
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.shortcuts import render, redirect
from django.template import loader, Context, RequestContext
from django.urls import reverse
from django.utils.datastructures import MultiValueDictKeyError

from talgoxe.models import AccessManager, Artikel, Exporter, Spole, UnsupportedFormat

@login_required
def index(request):
    template = loader.get_template('talgoxe/index.html')
    artiklar = Artikel.objects.all()
    context = { 'artiklar' : artiklar, 'pagetitle' : "Talgoxe – Svenskt dialektlexikon", 'checkboxes' : False }
    return HttpResponse(template.render(context, request))

@login_required # FIXME Något om användaren faktiskt är utloggad?
def create(request):
    AccessManager.check_edit_permission(request.user)
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
    artikel = Artikel.objects.create(lemma = nylemma, lemma_sortable = Artikel.get_lemma_sortable(nylemma), rang = rang)
    return HttpResponseRedirect(reverse('redigera', args = (artikel.id,)))

clipboards = {}

@login_required
def redigera(request, id):
    method = request.META['REQUEST_METHOD']
    if method == 'POST':
        AccessManager.check_edit_permission(request.user)
        artikel = Artikel.objects.get(id = id)
        artikel.update(request.POST)

    template = loader.get_template('talgoxe/redigera.html')
    artiklar = Artikel.objects.all()
    artikel = Artikel.objects.get(id = id)
    artikel.collect()
    username = request.user.username
    clipboard = ''
    if username in clipboards:
        clipboard = clipboards[username]

    context = {
        'artikel': artikel,
        'artiklar': artiklar,
        'pagetitle': "%s – redigera i Svenskt dialektlexikon" % artikel.lemma,
        'clipboard': clipboard
    }

    return HttpResponse(template.render(context, request))

@login_required
def delete(request, id):
    AccessManager.check_edit_permission(request.user)
    Spole.objects.filter(artikel_id = id).delete()
    Artikel.objects.get(id = id).delete()

    return HttpResponseRedirect(reverse('index'))

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
        return HttpResponse(template.render(context, request))

@login_required
def search(request): # TODO Fixa lista över artiklar när man POSTar efter omordning
    method = request.META['REQUEST_METHOD']
    if method == 'POST':
        AccessManager.check_edit_permission(request.user)
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
        return HttpResponse(template.render({ 'q' : 'NULL', 'uri' : uri }, request))
    if 'sök-överallt' in request.GET and request.GET['sök-överallt'] != 'None':
        sök_överallt = request.GET['sök-överallt']
    else:
        sök_överallt = None
    if sök_överallt:
        sök_överallt_eller_inte = 'söker överallt'
    else:
        sök_överallt_eller_inte = 'söker bara uppslagsord'
    artiklar = []
    search_stick_words = Artikel.objects.filter(lemma_sortable__contains = Artikel.get_lemma_sortable(söksträng))
    artiklar += search_stick_words
    if sök_överallt:
        spolar = Spole.objects.filter(text__contains = söksträng).select_related('artikel')
        artiklar += [spole.artikel for spole in spolar]
        articleIds = []
        for article in artiklar:
            articleIds.append(article.id)
        artiklar = []
        search_article_field_content = Artikel.objects.filter(id__in = articleIds)
        artiklar += search_article_field_content
    context = {
            'q' : söksträng,
            'artiklar' : artiklar,
            'pagetitle' : '%d sökresultat för ”%s” (%s)' % (len(artiklar), söksträng, sök_överallt_eller_inte),
            'uri' : uri,
            'sök_överallt' : sök_överallt,
        }

    return HttpResponse(template.render(context, request))

@login_required
def artikel(request, id):
    artikel = Artikel.objects.get(id = id)
    template = loader.get_template('talgoxe/artikel.html')
    artikel.collect()
    context = { 'artikel' : artikel, 'format' : format }

    return HttpResponse(template.render(context, request))

@login_required
def clipboard(request):
    userName = request.user.username
    clipboards[userName] = request.POST.get('clipboard');

    data = {
        'clipboardUpdated': True
    }
    return JsonResponse(data)

@login_required
def print_on_demand(request):
    # Artikel.update_lemma_sortable()
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
        context = { 'artiklar' : artiklar, 'redo' : True, 'titel' : 'Ditt urval på %d artiklar' % len(artiklar), 'pagetitle' : '%d artiklar' % len(artiklar) }
        template = loader.get_template('talgoxe/search.html')
    elif method == 'GET':
        artiklar = Artikel.objects.order_by('lemma', 'rang')
        bokstäver = [chr(i) for i in range(0x61, 0x7B)] + ['å', 'ä', 'ö']
        context = { 'artiklar' : artiklar, 'checkboxes' : True, 'bokstäver' : bokstäver, 'pagetitle' : '%d artiklar' % artiklar.count() }

    return HttpResponse(template.render(context, request))

@login_required
def print(request, format):
    if format not in ['pdf', 'odt', 'docx']:
        raise UnsupportedFormat(format)
    template = loader.get_template('talgoxe/download_document.html')
    exporter = Exporter(format)
    # exporter.export_letters()
    filepath = exporter.export(list(map(lambda s: s.strip(), request.GET['ids'].split(','))))
    context = { 'filepath' : filepath }

    return HttpResponse(template.render(context, request))

def easylogout(request):
    logout(request)
    template = loader.get_template("talgoxe/logout.html")
    return HttpResponse(template.render({ }, request))
