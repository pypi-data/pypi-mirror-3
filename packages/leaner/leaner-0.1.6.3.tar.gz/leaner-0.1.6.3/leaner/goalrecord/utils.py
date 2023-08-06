'''
Created on May 8, 2012

@author: brian
'''
from gargoyle import gargoyle

from django.conf import settings
from django.utils.importlib import import_module

from leaner.models import Participant

def get_user_status(request,switch_key):
    active = gargoyle.is_active(switch_key,request)
    participant = Participant.objects.get_or_enroll_user(
        request, active, switch_key)
    if participant:
        if participant.enrolled and not participant.opted_out:
            active = True
        elif participant.opted_out:
            active = False
    else:
        active = False
    return participant,active


LEANER_GOAL_RECORD_HELPER = import_module(getattr(settings,
    'LEANER_GOAL_RECORD_HELPER','leaner.goalrecord.rel_db'))

def record(switch_key,goal_type_slug,request):    
    active = gargoyle.is_active(switch_key,request)
    Participant.objects.get_or_enroll_user(
        request, active, switch_key)
    goal_record = LEANER_GOAL_RECORD_HELPER.GoalRecord(switch_key)
    return goal_record.record(goal_type_slug,request)