# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib import admin
from .models import Artikel, Spole, Typ

# Register your models here.
class TypAdmin(admin.ModelAdmin):
    list_display = ['kod', 'namn', 'skapat','uppdaterat']
    list_filter = ['namn','kod']

class SpoleAdmin(admin.ModelAdmin):
    list_display = ['artikel', 'typ', 'pos', 'text', 'skapat', 'uppdaterat']
    # extra_list_display = []
    # list_filter = []
    # extra_list_filter = []
    search_fields = ['artikel']
    # extra_search_fields = []
    # list_editable = []
    # raw_id_fields = []
    # inlines = []
    # filter_vertical = []
    # filter_horizontal = []
    # radio_fields = {}
    # prepopulated_fields = {}
    # formfield_overrides = {}
    # readonly_fields = []
    # exclude = ['hid']

class ArtikelAdmin(admin.ModelAdmin):
    list_display = ['lemma', 'rang', 'skapat', 'uppdaterat']
    # list_filter = ['lemma','rang']
    search_fields = ['lemma','rang']

admin.site.register(Typ, TypAdmin)
admin.site.register(Spole, SpoleAdmin)
admin.site.register(Artikel, ArtikelAdmin)
