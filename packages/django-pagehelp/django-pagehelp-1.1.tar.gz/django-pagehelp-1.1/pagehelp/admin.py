from django.contrib import admin
from pagehelp import models


class Page(admin.ModelAdmin):
    list_display = ('url', 'date_created', 'date_edited')


admin.site.register(models.Page, Page)
