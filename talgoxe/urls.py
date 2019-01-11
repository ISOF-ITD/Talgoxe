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
    url(r'^update_checked_articles', views.update_checked_articles, name = 'update_checked_articles'),
    url(r'^update_clipboard', views.update_clipboard, name = 'update_clipboard'),

    # HTML responses.
    url(r'^delete/(?P<id>\d+)$', views.delete, name = 'delete'),
    url(r'^edit/(?P<id>\d+)$', views.edit, name = 'edit'),
    url(r'^edit', views.edit, name = 'edit'),
    url(r'^logout', views.talgoxe_logout, name = 'talgoxe_logout'),
    url(r'^stickord/(?P<stickord>.+)$', views.artikel_efter_stickord, name = 'stickord'),
    url(r'^search$', views.search, name = 'search'),
    url(r'^artikel/(?P<id>\d+)?$', views.artikel, name = 'artikel'),
    url(r'^print-on-demand$', views.print_on_demand, name = 'print_on_demand'),
    url(r'^print-on-demand/(?P<format>.*)', views.print, name = 'print')
]
