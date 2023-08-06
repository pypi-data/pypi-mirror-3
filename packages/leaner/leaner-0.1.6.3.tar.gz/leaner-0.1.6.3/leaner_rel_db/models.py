'''
Created on Apr 24, 2012

@author: brian
'''
from django.db import models
from gargoyle.models import Switch
from leaner.models import GoalType, Participant
 
class GoalRecord(models.Model):
    goal_type = models.ForeignKey(GoalType)
    date_created = models.DateTimeField(auto_now_add=True)
    experiment = models.ForeignKey(Switch)
    participant = models.ForeignKey(Participant)