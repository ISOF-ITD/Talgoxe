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

from talgoxe.models import AccessManager, ArticleManager, ArticleSearchCriteria, Artikel, Exporter, Spole, UnsupportedFormat

userSettings = {}

class UserSettings:

    @staticmethod
    def get_articles_html(request):
        settings = UserSettings.get_settings(request)
        if 'articlesHtml' in settings:
            articles = settings['articlesHtml']
        else:
            articles = []
        return articles

    @staticmethod
    def get_clipboard(request):
        settings = UserSettings.get_settings(request)
        if 'clipboard' in settings:
            clipboard = settings['clipboard']
        else:
            clipboard = ''
        return clipboard

    @staticmethod
    def get_edit_article(request):
        settings = UserSettings.get_settings(request)
        if 'editArticle' in settings:
            editArticle = settings['editArticle']
        else:
            editArticle = None
        return editArticle

    @staticmethod
    def get_search_articles(request):
        settings = UserSettings.get_settings(request)
        if 'searchArticles' in settings:
            articles = settings['searchArticles']
        else:
            articles = []
        return articles

    @staticmethod
    def get_settings(request):
        userName = request.user.username
        if userName in userSettings:
            settings = userSettings[userName]
        else:
            settings = {}
            userSettings[userName] = settings
        return settings

    @staticmethod
    def update_clipboard(request, clipboard):
        settings = UserSettings.get_settings(request)
        settings['clipboard'] = clipboard

    @staticmethod
    def update_articles_html(request, articles):
        settings = UserSettings.get_settings(request)
        settings['articlesHtml'] = articles

    @staticmethod
    def update_edit_article(request, article):
        settings = UserSettings.get_settings(request)
        settings['editArticle'] = article

    @staticmethod
    def update_search_articles(request, articles):
        settings = UserSettings.get_settings(request)
        settings['searchArticles'] = articles
        for article in articles:
            article.checked = False

@login_required
def artikel(request, id):
    artikel = Artikel.objects.get(id = id)
    template = loader.get_template('talgoxe/artikel.html')
    artikel.collect()
    context = { 'current_article' : artikel,
                'current_page' : 'artikel',
                'format' : format }
    return HttpResponse(template.render(context, request))

@login_required
def artikel_efter_stickord(request, stickord):
    artiklar = Artikel.objects.filter(lemma = stickord)
    # TODO: 0!
    if len(artiklar) == 1:
        return HttpResponseRedirect(reverse('redigera', args = (artiklar.first().id,)))
    else:
        template = loader.get_template('talgoxe/stickord.html')
        context = {
            'artiklar' : artiklar,
            'current_article': artikel,
            'current_page': 'stickord',
        }
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

@login_required
def delete(request, id):
    AccessManager.check_edit_permission(request.user)
    Spole.objects.filter(artikel_id = id).delete()
    Artikel.objects.get(id = id).delete()
    UserSettings.update_edit_article(request, None)

    return HttpResponseRedirect(reverse('redigera'))

def easylogout(request):
    logout(request)
    template = loader.get_template("talgoxe/logout.html")
    return HttpResponse(template.render({ }, request))

@login_required
def get_articles_by_search_criteria(request):
    compare_type = request.POST.get('searchCriteriaArray[0][compare_type]')
    search_string = request.POST.get('searchCriteriaArray[0][search_string]')
    search_type = request.POST.get('searchCriteriaArray[0][search_type]')
    search_criteria = ArticleSearchCriteria()
    search_criteria.compare_type = compare_type
    search_criteria.search_string = search_string
    search_criteria.search_type = search_type
    articles = ArticleManager.get_articles_by_search_criteria(search_criteria)
    UserSettings.update_search_articles(request, articles)

    articles_dictionary = {}
    articles_array = []

    for article in articles:
        data = {
            'lemma': article.lemma,
            'id' : article.id,
            'rank' : article.rang
        }
        articles_array.append(data)

    articles_dictionary["articles"] = articles_array
    return JsonResponse(articles_dictionary, safe=False)

def get_article_html(request, article):
    string_builder = []
    string_builder.append("<p>")
    template = loader.get_template('talgoxe/artikel.html')
    context = {
        'artikel': article,
    }
    string_builder.append(template.render(context, request))
    string_builder.append("</p>")
    return ''.join(string_builder)

@login_required
def get_articles_html(request):
    # Get articles.
    articles = []
    article_ids = request.POST.getlist('showArticleIds[]')
    articles_database = Artikel.objects.filter(id__in=article_ids)
    articles += articles_database
    UserSettings.update_articles_html(request, articles)

    # Get articles as HTML.
    string_builder = []
    if (len(articles) <= 1):
        string_builder.append("<h2>Artikel</h2>")
    if (len(articles) > 1):
        string_builder.append("<h2>Artiklar</h2>")
    string_builder.append('<div class="show-articles-column">')
    for article in articles:
        article.collect()
        string_builder.append(get_article_html(request, article))
    string_builder.append("</div>")

    data = {
        'articlesHtml': ''.join(string_builder)
    }
    return JsonResponse(data)

@login_required
def get_clipboard(request):
    data = {
        'clipboard': UserSettings.get_clipboard(request)
    }
    return JsonResponse(data)

@login_required
def index(request):
    article = UserSettings.get_edit_article(request)
    if (article is None):
        return HttpResponseRedirect(reverse('redigera'))
    else:
        return HttpResponseRedirect(reverse('redigera', args=(article.id,)))

@login_required
def print(request, format):
    if format not in ['pdf', 'odt', 'docx']:
        raise UnsupportedFormat(format)
    template = loader.get_template('talgoxe/download_document.html')
    exporter = Exporter(format)
    # exporter.export_letters()
    filepath = exporter.export(list(map(lambda s: s.strip(), request.GET['ids'].split(','))))
    context = {'current_article' : UserSettings.get_edit_article(request),
               'print_on_demand': True,
               'filepath' : filepath }

    return HttpResponse(template.render(context, request))

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
        context = { 'current_article' : UserSettings.get_edit_article(request),
                    'artiklar' : artiklar,
                    'redo' : True,
                    'titel' : 'Ditt urval på %d artiklar' % len(artiklar),
                    'pagetitle' : '%d artiklar' % len(artiklar),
                    'print_on_demand': True }
        template = loader.get_template('talgoxe/search.html')
    elif method == 'GET':
        artiklar = Artikel.objects.order_by('lemma', 'rang')
        bokstäver = [chr(i) for i in range(0x61, 0x7B)] + ['å', 'ä', 'ö']
        context = { 'current_article' : UserSettings.get_edit_article(request),
                    'artiklar' : artiklar,
                    'checkboxes' : True,
                    'bokstäver' : bokstäver,
                    'pagetitle' : '%d artiklar' % artiklar.count(),
                    'print_on_demand': True }

    return HttpResponse(template.render(context, request))

@login_required
def redigera(request, id = None):
    artikel = None
    method = request.META['REQUEST_METHOD']
    if method == 'POST':
        AccessManager.check_edit_permission(request.user)
        if (id is None):
            artikel = Artikel.create(request.POST)
            return HttpResponseRedirect(reverse('redigera', args=(artikel.id)))
        else:
            artikel = Artikel.objects.get(id=id)
            artikel.update(request.POST)

    template = loader.get_template('talgoxe/redigera.html')
    pageTitle = 'Svenskt dialektlexikon'
    if ((artikel is None) and (not (id is None))):
        # Get article information.
        artikel = Artikel.objects.get(id=id)
        artikel.collect()
        pageTitle = artikel.lemma + "- " + pageTitle
        UserSettings.update_edit_article(request, artikel)

    if (len(UserSettings.get_articles_html(request)) < 1):
        articles = []
        articles.append(artikel)
        UserSettings.update_articles_html(request, articles)

    if (artikel is None):
        context = {
            'articles': UserSettings.get_articles_html(request),
            'current_article' : UserSettings.get_edit_article(request),
            'current_page': 'redigera',
            'edit_artikel': artikel,
            'pagetitle': pageTitle,
            'clipboard': None,
            'create_article' : True,
            'search_articles' : UserSettings.get_search_articles(request)
        }
    else:
        context = {
            'articles': UserSettings.get_articles_html(request),
            'current_article' : UserSettings.get_edit_article(request),
            'current_page': 'redigera',
            'edit_artikel': artikel,
            'pagetitle': pageTitle,
            'clipboard': None,
            'edit_article' : True,
            'search_articles': UserSettings.get_search_articles(request)
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
            'current_article' : UserSettings.get_edit_article(request),
            'current_page': 'search',
            'q' : söksträng,
            'artiklar' : artiklar,
            'pagetitle' : '%d sökresultat för ”%s” (%s)' % (len(artiklar), söksträng, sök_överallt_eller_inte),
            'uri' : uri,
            'sök_överallt' : sök_överallt,
        }

    return HttpResponse(template.render(context, request))

@login_required
def update_checked_articles(request):
    article_ids_dictionary = {}
    article_ids = request.POST.getlist('checkedArticleIds[]')
    for article_id in article_ids:
        article_ids_dictionary[int(article_id)] = article_id
    for article in UserSettings.get_search_articles(request):
        article.checked = (article.id in article_ids_dictionary)
    articles = UserSettings.get_search_articles(request)

    data = {
        'checkedArticlesUpdated': True
    }
    return JsonResponse(data)

@login_required
def update_clipboard(request):
    UserSettings.update_clipboard(request, request.POST.get('clipboard'))
    data = {
        'clipboardUpdated': True
    }
    return JsonResponse(data)
