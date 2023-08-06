'''
Created on Mar 2, 2012

@author: brian
'''

from django.db import models
from django.conf import settings
from django.contrib import messages
from django.core.urlresolvers import reverse
from django.template.defaultfilters import mark_safe
from gargoyle.models import Switch
from utils import get_key

__all__ = ('Participant','GoalType')
   
LEANER_USE_MESSAGES = getattr(settings, 'LEANER_USE_MESSAGES',True)

class ParticipantManager(models.Manager):
    
    def get_or_enroll_user(self,request,active,switch_key,**kwargs):
        '''
        Retrieves a Participant or creates one and assigns them to test or 
        control groups
        
        @param request: Django Request object
        @param experiment_slug: Slug for Experiment object
        '''
        user = request.user
        if user.is_authenticated():
            user_key = get_key(user, switch_key)
            try:
                return self.get(user_key=user_key,switch__key=switch_key)
            except Participant.DoesNotExist:
                try:
                    switch = Switch.objects.get(key=switch_key)
                except Switch.DoesNotExist:
                    return None
                use_messages = LEANER_USE_MESSAGES
                if use_messages and active:
                    messages.info(request,
                        mark_safe(
                            'You were selected for the {0} group. <a href="{1}">More info</a>'\
                            .format(switch.label,
                                    reverse('leaner_switch_detail',args=[switch_key]))),
                        fail_silently=True)
                return self.create(user_key=user_key,enrolled=active,
                        switch=switch)
        return None

class Participant(models.Model):
    '''
    Model containing non user specific information about a user and the switch 
    he/she are associated with.
    
    @param user_key: Key used to identify a user without actually identifying 
    an user
    
    @param enrolled: Whether a user is enrolled in a switch or not.
    
    @param date_created: Date when the distinction was made when the user would
    be enrolled in the switch or not
    
    @param opted_out: Whether the user explicitly opted out of the switch
      
    '''
    user_key = models.CharField(unique=True,max_length=100)
    enrolled = models.BooleanField(default=False)
    date_created = models.DateTimeField(auto_now_add=True)
    opted_out = models.BooleanField(default=False)
    switch = models.ForeignKey(Switch)
    objects = ParticipantManager()
    
    def __unicode__(self):
        return self.user_key
    
    @property
    def switch_label(self):
        return '{0} ({1})'.format(self.switch.label,self.switch.key)
    
class GoalType(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)
    switch = models.ForeignKey(Switch)
    
    def __unicode__(self):
        return self.name