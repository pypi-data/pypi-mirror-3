'''
Created on Apr 24, 2012

@author: brian
'''
from django.conf import settings
from gargoyle.models import Switch
from leaner.models import GoalType

__all__ = ('BaseGoalRecord',)
LEANER_SESSION_PREFIX = getattr(settings, 'LEANER_SESSION_PREFIX','LEANER')

class BaseGoalRecord(object):
    '''
    Base Goal Record class. Stubs out all methods required by GoalRecord 
    classes.
    @param switch_key: The "key" attribute of the gargoyle Switch model 
    instance you are referencing.
    '''
    
    def __init__(self,switch_key):
        self.switch_key = switch_key
    
    @property    
    def switch(self):
        return self.get_switch()
    
    @property
    def goal_types(self):
        return self.get_goal_types()

    def get_switch(self):
        return Switch.objects.get_or_create(key=self.switch_key)
        
    def get_goal_types(self):
        return GoalType.objects.filter(switch=self.switch)
    
    def get_group_count(self,goal_type_slug,active=True,**filters):
        raise NotImplementedError
    
    def _record(self,goal_type_slug,request):
        raise NotImplementedError
    
    def record(self,goal_type_slug,request):
        session_key = '{0}_{1}'.format(
            LEANER_SESSION_PREFIX,goal_type_slug.replace('-','_'))
        goal_session = request.session.get(session_key)
        if not goal_session:
            record = self._record(goal_type_slug, request)
            if record:
                request.session[session_key] = True
            return record
        return False
    
    