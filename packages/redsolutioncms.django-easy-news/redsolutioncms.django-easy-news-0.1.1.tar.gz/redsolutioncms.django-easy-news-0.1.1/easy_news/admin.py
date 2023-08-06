# -*- coding: utf-8 -*-
from django.contrib import admin
from django import forms
from easy_news.models import News

class NewsForm(forms.ModelForm):
    class Meta:
        model = News
    title = forms.CharField(widget=forms.Textarea(attrs={'rows': 3}), max_length=500)

class NewsAdmin(admin.ModelAdmin):
    list_display = ['title', 'date', 'show', ]
    prepopulated_fields = {'slug': ('title',)}
    form = NewsForm

try:
    admin.site.register(News, NewsAdmin)
except admin.sites.AlreadyRegistered:
    pass
