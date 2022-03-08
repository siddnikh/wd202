from django.contrib import admin

# Register your models here.
from tasks.models import Task, History, Report

class HistoryAdmin(admin.ModelAdmin):
    readonly_fields = ('date_of_update','id')

admin.sites.site.register(Task)
admin.sites.site.register(Report)
admin.sites.site.register(History, HistoryAdmin)