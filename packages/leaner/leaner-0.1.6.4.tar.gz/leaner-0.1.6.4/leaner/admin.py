'''
Created on Mar 6, 2012

@author: brian
'''
from django.contrib import admin

from models import *

class ParticipantAdmin(admin.ModelAdmin):
    list_display = ('user_key','enrolled','date_created','opted_out','switch_label')
    list_filter = ('enrolled','opted_out',)
    
class GoalTypeAdmin(admin.ModelAdmin):
    list_display = ('name','slug')
    prepopulated_fields = {"slug": ("name",)}
    
admin.site.register(Participant,ParticipantAdmin)
admin.site.register(GoalType,GoalTypeAdmin)
