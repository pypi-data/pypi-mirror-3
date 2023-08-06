# -*- coding: utf-8 -*-
from django.contrib import admin
from prospect.models import Prospect, Field, Activity

class ProspectAdmin(admin.ModelAdmin):
    list_display=( 'company_name', 'first_name', 'last_name')

admin.site.register(Prospect, ProspectAdmin)
admin.site.register(Field)
admin.site.register(Activity)
