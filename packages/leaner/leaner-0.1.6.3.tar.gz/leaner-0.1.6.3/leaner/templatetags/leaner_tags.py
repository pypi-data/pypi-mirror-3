'''
Created on Mar 5, 2012

@author: brian
'''
from django.conf import settings
from django import template
from django.utils.importlib import import_module

from classytags.core import Tag,Options
from classytags.arguments import Argument,MultiValueArgument

from ..goalrecord.utils import get_user_status

register = template.Library()

LEANER_GOAL_RECORD_HELPER = getattr(settings, 'LEANER_GOAL_RECORD_HELPER',
    'leaner.goalrecord.rel_db')

class LeanerTagError(Exception):
    pass

class IfSwitch(Tag):
    name = 'ifswitch'
    options = Options(
        Argument('switch_key',resolve=False),
        MultiValueArgument('instances',required=False),
        'as',
        Argument('context_name',required=True,resolve=False),
                      )
    
    def render_tag(self, context, switch_key,instances=(),context_name=None,**kwargs):
        try:
            instances.append(context['request'])
            request = context['request']
        except KeyError:
            raise LeanerTagError(
                'The request object must be part of the '\
                'context given to the ifswitch tag.')
        participant,active = get_user_status(request, switch_key)
            
        context[context_name] = active
        return ''

register.tag(IfSwitch)

@register.inclusion_tag('leaner/templatetags/goal_record_report.html')
def goal_record_report(switch_key,goal_type_slug,in_group,group_user_count):
    helper_class = import_module(
        LEANER_GOAL_RECORD_HELPER).GoalRecord(switch_key)
    
    return {'group_count':helper_class.get_group_count(goal_type_slug,bool(in_group)),
            'total_group_count':group_user_count}