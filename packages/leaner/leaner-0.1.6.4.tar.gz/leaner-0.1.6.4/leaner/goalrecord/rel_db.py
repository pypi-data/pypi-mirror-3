'''
Created on Apr 24, 2012

@author: brian
'''
from base import BaseGoalRecord
from leaner_rel_db.models import GoalRecord as RelGoalRecord

from leaner.models import GoalType

from leaner.goalrecord.utils import get_user_status

class GoalRecord(BaseGoalRecord):
    
    def _record(self, goal_type_slug, request):
        if not request.user.is_authenticated():
            return False
        try:
            goal_type = GoalType.objects.get(slug=goal_type_slug)
        except (GoalType.DoesNotExist):
            return None
        participant,active = get_user_status(request, self.switch_key)
        if participant:
            RelGoalRecord.objects.create(goal_type=goal_type,experiment=participant.switch,
                participant=participant)
            return True
        return False
        
    def get_group_count(self, goal_type_slug,active=True,**filters):
        return RelGoalRecord.objects.filter(goal_type__slug=goal_type_slug,
            participant__enrolled=active).count()
            