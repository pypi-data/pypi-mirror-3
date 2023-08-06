'''
Created on Apr 24, 2012

@author: brian
'''
import time

from boto import connect_dynamodb
from boto.dynamodb.condition import BEGINS_WITH
from django.conf import settings
from gargoyle.models import Switch
from base import BaseGoalRecord
from leaner.models import GoalType,Participant
from leaner.utils import get_key

LEANER_GOAL_TABLE = getattr(settings, 'LEANER_GOAL_TABLE',None)

class GoalRecord(BaseGoalRecord):
    
    def _record(self, goal_type_slug, request):
        user = request.user
        if not user.is_authenticated():
            return False
        try:
            exp = Switch.objects.get(key=self.switch_key)
            goal_type = GoalType.objects.get(slug=goal_type_slug)
            user_key = get_key(user, self.switch_key)
            participant = Participant.objects.get(user_key=user_key,
                switch=exp)
        except (Switch.DoesNotExist,GoalType.DoesNotExist):
            return False
        if not isinstance(participant, Participant):
            return False

        dyndb = connect_dynamodb(settings.AWS_ACCESS_KEY,
            settings.AWS_SECRET_KEY)
        table = dyndb.get_table(LEANER_GOAL_TABLE)
        item_data = dict(switch_key=self.switch_key,active=participant.active,
            goal_type_id=goal_type.pk,experiment_id=exp.pk,participant_id=participant.pk,
            user_key=user_key)
        
        timestamp = int(time.time())
        table.new_item(str(goal_type_slug),'{0}-{1}'.format(
                participant.active,timestamp), item_data)
        return True
        
    def get_group_count(self, goal_type_slug, active=True, **filters):
        dyndb = connect_dynamodb(settings.AWS_ACCESS_KEY,
            settings.AWS_SECRET_KEY)
        table = dyndb.get_table(LEANER_GOAL_TABLE)
        table.query(goal_type_slug, BEGINS_WITH(str(active)))