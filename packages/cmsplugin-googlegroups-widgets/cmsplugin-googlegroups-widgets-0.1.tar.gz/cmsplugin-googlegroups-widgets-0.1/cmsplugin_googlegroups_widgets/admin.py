# coding: utf-8
import datetime
from models import GoogleGroup
from django.contrib import admin

class GoogleGroupAdmin(admin.ModelAdmin):
    list_display = ("group_name",)
    search_fields = ["group_name"]

admin.site.register(GoogleGroup, GoogleGroupAdmin)
