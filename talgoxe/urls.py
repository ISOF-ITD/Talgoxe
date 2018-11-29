# encoding: UTF-8

from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^$', views.index, name = 'index'),
    url(r'^get_clipboard', views.get_clipboard, name = 'get_clipboard'),
    url(r'^update_clipboard', views.update_clipboard, name = 'update_clipboard'),
    url(r'^create', views.create, name = 'create'),
    url(r'^redigera/create', views.create, name = 'create'),
    url(r'^delete/(?P<id>\d+)$', views.delete, name = 'delete'),
    url(r'^redigera/(?P<id>\d+)$', views.redigera, name = 'redigera'),
    url(r'^stickord/(?P<stickord>.+)$', views.artikel_efter_stickord, name = 'stickord'),
    url(r'^search$', views.search, name = 'search'),
    url(r'^artikel/(?P<id>\d+)?$', views.artikel, name = 'artikel'),
    url(r'^print-on-demand$', views.print_on_demand, name = 'print_on_demand'),
    url(r'^print-on-demand/(?P<format>.*)', views.print, name = 'print'),
    url(r'^logout', views.easylogout, name = 'easylogout'),
]
