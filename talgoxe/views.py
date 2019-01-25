# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import os

from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseRedirect, Http404, JsonResponse
from django.template import loader
from django.urls import reverse
from re import match
from talgoxe.AccessManager import AccessManager
from talgoxe.ArticleManager import ArticleManager
from talgoxe.common_functions import *
from talgoxe.models import ArticleSearchCriteria, Exporter, UnsupportedFormat
from talgoxe.UserSettings import UserSettings


@login_required
def delete(request, id):
    AccessManager.check_edit_permission(request.user)
    ArticleManager.delete_article(id)
    UserSettings.update_edit_article(request, None)
    return HttpResponseRedirect(reverse('edit'))


@login_required
def edit(request, id = None):
    article = None
    if (request.META['REQUEST_METHOD'] == 'POST'):
        AccessManager.check_edit_permission(request.user)
        if (id is None):
            # Create new article.
            article = ArticleManager.create_article(request.POST)
            UserSettings.update_edit_article(request, article)
            return HttpResponseRedirect(reverse('edit', args=(article.id,)))
        else:
            # Update existing article.
            article = ArticleManager.update_article(id, request.POST)
            UserSettings.update_articles_cache(request)

    template = loader.get_template('talgoxe/edit.html')
    page_title = 'Svenskt dialektlexikon'
    if ((article is None) and (not (id is None))):
        # Get article information.
        article = ArticleManager.get_article(id)
        page_title = article.lemma + " - " + page_title
        UserSettings.update_edit_article(request, article)

    if (not (UserSettings.has_articles_html(request))):
        # Show edited article in article view area.
        UserSettings.update_article_html(request, article)

    search_criteria = UserSettings.get_search_criteria(request)
    context = {
        'articles_html' : UserSettings.get_articles_html(request),
        'current_article' : UserSettings.get_edit_article(request),
        'has_articles_html' : UserSettings.has_articles_html(request),
        'page_title' : page_title,
        'search_articles' : UserSettings.get_search_articles(request),
        'search_criteria_one' : search_criteria[0],
        'search_criteria_two' : search_criteria[1],
        'search_criteria_three' : search_criteria[2]
    }
    if (article is None):
        context['is_create_article_page'] = True
    else:
        context['is_edit_article_page'] = True

    return HttpResponse(template.render(context, request))


@login_required
def edit_select(request, lemma):
    articles = ArticleManager.get_articles_by_lemma(lemma)

    if (len(articles) == 0):
        # No article matches lemma. Go to create article.
        return HttpResponseRedirect(reverse('edit'))

    if (len(articles) == 1):
        # Edit found article.
        return HttpResponseRedirect(reverse('edit', args = (articles[0].id,)))

    # Let the user select among articles with the same lemma.
    # Lemma 'drönta' can be used to trigger this section of the code.
    template = loader.get_template('talgoxe/edit_select.html')
    page_title = lemma + ' - Svenskt dialektlexikon'
    context = {
        'articles' : articles,
        'current_article' : UserSettings.get_edit_article(request),
        'has_articles_html': UserSettings.has_articles_html(request),
        'is_edit_article_page': True,
        'page_title': page_title
    }
    return HttpResponse(template.render(context, request))


@login_required
def get_article_html(request, id):
    # This method is used in AJAX-requests and the returned HTML is used as data.
    article = ArticleManager.get_article(id)
    template = loader.get_template('talgoxe/article.html')
    context = { 'article' : article, 'format' : format }
    return HttpResponse(template.render(context, request))


def get_article_html_by_article(request, article):
    string_builder = []
    string_builder.append("<p>")
    template = loader.get_template('talgoxe/article.html')
    context = {
        'article' : article,
    }
    string_builder.append(template.render(context, request))
    string_builder.append("</p>")
    return ''.join(string_builder)


@login_required
def get_articles_by_search_criteria(request):
    search_criteria_list = [];
    compare_type = request.POST.get('searchCriteriaArray[0][compare_type]')
    search_string = request.POST.get('searchCriteriaArray[0][search_string]')
    search_type = request.POST.get('searchCriteriaArray[0][search_type]')
    search_criteria = ArticleSearchCriteria()
    search_criteria.compare_type = compare_type
    search_criteria.search_string = search_string
    search_criteria.search_type = search_type
    search_criteria_list.append(search_criteria)
    compare_type = request.POST.get('searchCriteriaArray[1][compare_type]')
    search_string = request.POST.get('searchCriteriaArray[1][search_string]')
    search_type = request.POST.get('searchCriteriaArray[1][search_type]')
    search_criteria = ArticleSearchCriteria()
    search_criteria.compare_type = compare_type
    search_criteria.search_string = search_string
    search_criteria.search_type = search_type
    search_criteria_list.append(search_criteria)
    compare_type = request.POST.get('searchCriteriaArray[2][compare_type]')
    search_string = request.POST.get('searchCriteriaArray[2][search_string]')
    search_type = request.POST.get('searchCriteriaArray[2][search_type]')
    search_criteria = ArticleSearchCriteria()
    search_criteria.compare_type = compare_type
    search_criteria.search_string = search_string
    search_criteria.search_type = search_type
    search_criteria_list.append(search_criteria)
    UserSettings.update_search_criteria(request, search_criteria_list)
    articles = ArticleManager.get_articles_by_search_criteria(search_criteria_list)
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
    return JsonResponse(articles_dictionary, safe = False)


@login_required
def get_articles_html(request):
    # Get articles.
    articles = ArticleManager.get_articles_by_ids(request.POST.getlist('showArticleIds[]'))
    UserSettings.update_articles_html(request, articles)

    # Get articles as HTML.
    string_builder = []
    if (len(articles) <= 1):
        string_builder.append("<h2>Artikel</h2>")
    if (len(articles) > 1):
        string_builder.append("<h2>Artiklar</h2>")
    string_builder.append('<div class="show-articles-column">')
    for article in articles:
        string_builder.append(get_article_html_by_article(request, article))
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
def get_file(request, format):
    if (format not in ['pdf', 'odt', 'docx']):
        raise UnsupportedFormat(format)
    template = loader.get_template('talgoxe/get_file.html')
    exporter = Exporter(format)
    # exporter.export_letters()
    file_path = exporter.export(list(map(lambda s: s.strip(), request.GET['ids'].split(','))))

    context = {
        'current_article' : UserSettings.get_edit_article(request),
        'filepath' : file_path,
        'has_articles_html': UserSettings.has_articles_html(request),
        'is_select_articles_page': True
    }
    return HttpResponse(template.render(context, request))


def get_no_file():
    response = HttpResponse('Inga artiklar att visa.', content_type = "application/text")
    response['Content-Disposition'] = 'inline; filename=IngaArtiklarAttVisa'
    return response


@login_required
def get_odf_file(request):
    articles = UserSettings.get_articles_html(request)
    if (not (UserSettings.has_articles_html(request))):
        return get_no_file()

    exporter = Exporter('odt')
    file_path = exporter.export_articles(articles, request.user.username)
    if os.path.exists(file_path):
        with open(file_path, 'rb') as file_handle:
            response = HttpResponse(file_handle.read(), content_type = "application/vnd.oasis.opendocument.text")
            response['Content-Disposition'] = 'inline; filename=' + os.path.basename(file_path)
            return response
    raise Http404


@login_required
def get_pdf_file(request):
    articles = UserSettings.get_articles_html(request)
    if (not (UserSettings.has_articles_html(request))):
        return get_no_file()

    exporter = Exporter('pdf')
    file_path = exporter.export_articles(articles, request.user.username)
    if os.path.exists(file_path):
        with open(file_path, 'rb') as file_handle:
            response = HttpResponse(file_handle.read(), content_type = "application/pdf")
            response['Content-Disposition'] = 'inline; filename=' + os.path.basename(file_path)
            return response
    raise Http404


@login_required
def get_word_file(request):
    articles = UserSettings.get_articles_html(request)
    if (not (UserSettings.has_articles_html(request))):
        return get_no_file()

    exporter = Exporter('docx')
    file_path = exporter.export_articles(articles, request.user.username)
    if os.path.exists(file_path):
        with open(file_path, 'rb') as file_handle:
            response = HttpResponse(file_handle.read(), content_type = "application/vnd.openxmlformats-officedocument.wordprocessingml.document")
            response['Content-Disposition'] = 'inline; filename=' + os.path.basename(file_path)
            return response
    raise Http404


@login_required
def index(request):
    if (UserSettings.has_edit_article(request)):
        article = UserSettings.get_edit_article(request)
        return HttpResponseRedirect(reverse('edit', args = (article.id,)))
    else:
        return HttpResponseRedirect(reverse('edit'))


@login_required
def reordering(request):
    # Get article ids.
    article_ids = []
    for article in request.POST:
        if match('^artikel-', article):
            article_ids.append(int(article.replace('artikel-', '')))

    if (request.META['REQUEST_METHOD'] == 'POST'):
        # Update article order.
        AccessManager.check_edit_permission(request.user)
        ArticleManager.update_article_order(article_ids)

    template = loader.get_template('talgoxe/reordering.html')
    articles = ArticleManager.get_articles_by_ids(article_ids)
    context = {
        'articles' : articles,
        'current_article' : UserSettings.get_edit_article(request),
        'has_articles_html' : UserSettings.has_articles_html(request),
        'is_select_articles_page' : True,
        'page_title' : f'{len(articles)} artiklar',
        'titel': f'Ditt urval på {len(articles)} artiklar'
    }
    return HttpResponse(template.render(context, request))


@login_required
def select_articles(request):
    # Artikel.update_lemma_sortable()
    method = request.META['REQUEST_METHOD']
    if (method == 'POST'):
        articles = []
        for article_selection in request.POST:
            article_id = match('selected-(\d+)', article_selection)
            letter = match('bokstav-(.)', article_selection)
            if article_id:
                articles.append(ArticleManager.get_article(int(article_id.group(1), False)))
            elif letter:
                articles += ArticleManager.get_articles_by_letter(letter.group(1), False)

        template = loader.get_template('talgoxe/reordering.html')
        context = {
            'articles' : articles,
            'current_article' : UserSettings.get_edit_article(request),
            'has_articles_html': UserSettings.has_articles_html(request),
            'is_select_articles_page': True,
            'page_title' : f'{len(articles)} artiklar',
            'titel': f'Ditt urval på {len(articles)} artiklar'
        }

    elif (method == 'GET'):
        articles = ArticleManager.get_articles(False)
        alphabet = get_swedish_alphabet()

        template = loader.get_template('talgoxe/select_articles.html')
        context = {
            'alphabet' : alphabet,
            'articles' : articles,
            'checkboxes' : True,
            'current_article' : UserSettings.get_edit_article(request),
            'has_articles_html' : UserSettings.has_articles_html(request),
            'is_select_articles_page' : True,
            'page_title' : f'{len(articles)} artiklar'
        }

    return HttpResponse(template.render(context, request))


def talgoxe_logout(request):
    logout(request)
    template = loader.get_template("talgoxe/logout.html")
    return HttpResponse(template.render({ }, request))


@login_required
def reset_article_search_criteria(request):
    UserSettings.update_search_criteria(request, None)
    data = {
        'articleSearchCriteriaUpdated': True
    }
    return JsonResponse(data)


@login_required
def update_checked_articles(request):
    article_ids_dictionary = {}
    article_ids = request.POST.getlist('checkedArticleIds[]')
    for article_id in article_ids:
        article_ids_dictionary[int(article_id)] = article_id
    for article in UserSettings.get_search_articles(request):
        article.checked = (article.id in article_ids_dictionary)

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
