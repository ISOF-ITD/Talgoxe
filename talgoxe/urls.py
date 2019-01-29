# encoding: UTF-8

from django.conf.urls import url

from . import views

urlpatterns = [
    # Default HTML response.
    url(r'^$', views.index, name = 'index'),

    # Ajax requests with JSON responses.
    url(r'^get_articles_by_search_criteria', views.get_articles_by_search_criteria, name = 'get_articles_by_search_criteria'),
    url(r'^get_articles_html', views.get_articles_html, name = 'get_articles_html'),
    url(r'^get_clipboard', views.get_clipboard, name = 'get_clipboard'),
    url(r'^get_odf_file', views.get_odf_file, name = 'get_odf_file'),
    url(r'^get_pdf_file', views.get_pdf_file, name = 'get_pdf_file'),
    url(r'^get_word_file', views.get_word_file, name = 'get_word_file'),
    url(r'^get_word_file', views.get_word_file, name = 'get_word_file'),
    url(r'^reset_article_search_criteria', views.reset_article_search_criteria, name = 'reset_article_search_criteria'),
    url(r'^update_checked_articles', views.update_checked_articles, name = 'update_checked_articles'),
    url(r'^update_clipboard', views.update_clipboard, name = 'update_clipboard'),

    # HTML responses.
    url(r'^delete/(?P<id>\d+)$', views.delete, name = 'delete'),
    url(r'^edit_select/(?P<lemma>.+)$', views.edit_select, name = 'edit_select'),
    url(r'^edit/(?P<id>\d+)$', views.edit, name = 'edit'),
    url(r'^edit', views.edit, name = 'edit'),
    url(r'^get_article_html/(?P<id>\d+)?$', views.get_article_html, name = 'get_article_html'),
    url(r'^get_file/(?P<format>.*)', views.get_file, name = 'get_file'),
    url(r'^logout', views.talgoxe_logout, name = 'talgoxe_logout'),
    url(r'^reordering', views.reordering, name = 'reordering'),
    url(r'^select_articles', views.select_articles, name = 'select_articles')
]
