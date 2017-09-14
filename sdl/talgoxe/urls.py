# encoding: UTF-8

from django.conf.urls import url

from . import views

stickord_regexp = ur'^stickord/(?P<stickord>[ TSOHF2a-zåäö()-]+)'
urlpatterns = [
    url(r'^$', views.index, name = 'index'),
    url(stickord_regexp + ur'$', views.stickord, name = 'stickord'),
    url(stickord_regexp + ur'/print', views.print_stickord, name = 'print_stickord'),
    url(r'^print$', views.printing, name = 'printing'),
]
