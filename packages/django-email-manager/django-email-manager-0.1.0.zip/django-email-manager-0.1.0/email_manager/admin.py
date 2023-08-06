# -*- coding: utf-8 -*-
from django.contrib import admin

from email_manager.models import EmailLog, EmailStatistics, EmailDatabase
from email_manager.feature_update_statistics import update_statistics


#Useful for development
#from django.conf import settings
#if settings.DEBUG: # precaution
#    from django.contrib.auth.models import Permission
#    admin.site.register(Permission)


class EmailLogAdmin(admin.ModelAdmin):
    list_display = ('id', 'email', 'subject', 'date')
    list_filter = ('date',)
    ordering = ('date',)
    search_fields = ('email', 'subject')
    

def update_statistics(modeladmin, request, queryset):
    update_statistics()
update_statistics.short_description = "Update statistics"

    
class EmailStatisticsAdmin(admin.ModelAdmin):
    actions = [update_statistics]
    list_display = ('id', 'date', 'quantity',)
    ordering = ('date',)
    search_fields = ('date',)
    
    
class EmailDatabaseAdmin(admin.ModelAdmin):
    list_display = ('id', 'email')
    ordering = ('id',)
    search_fields = ('email',)
    
    
admin.site.register(EmailLog, EmailLogAdmin)
admin.site.register(EmailStatistics, EmailStatisticsAdmin)
admin.site.register(EmailDatabase, EmailDatabaseAdmin)
    