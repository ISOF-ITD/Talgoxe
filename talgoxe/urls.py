# encoding: UTF-8

from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^$', views.index, name = 'index'),
    url('create', views.create, name = 'create'),
    url(r'^redigera/(?P<id>\d+)$', views.redigera, name = 'redigera'),
    url(r'^stickord/(?P<stickord>.+)$', views.artikel_efter_stickord, name = 'stickord'),
    url(r'^search$', views.search, name = 'search'),
    url(r'^artikel/(?P<id>\d+)?$', views.artikel, name = 'artikel'),
    url(r'print-on-demand$', views.print_on_demand, name = 'print_on_demand'),
    url(r'print-on-demand/(?P<format>.*)', views.print, name = 'print'),
    url(r'logout', views.easylogout, name = 'easylogout'),
]
