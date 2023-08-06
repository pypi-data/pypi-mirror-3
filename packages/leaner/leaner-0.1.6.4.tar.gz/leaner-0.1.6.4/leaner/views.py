'''
Created on Apr 30, 2012

@author: brian
'''

from django.views.generic import DetailView
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import user_passes_test
from django.contrib.auth.models import User
from django.conf import settings
from django.http import Http404
from gargoyle.models import Switch

from models import GoalType,Participant
from goalrecord.utils import get_user_status,record

LEANER_DEBUG = getattr(settings, 'LEANER_DEBUG',False)

class BaseSwitchDetailView(DetailView):
    model = Switch
    slug_field = 'key'
    template_name = 'leaner/switch-detail.html'

class SwitchDetailView(BaseSwitchDetailView):
    
    def get_context_data(self, **kwargs):
        content = BaseSwitchDetailView.get_context_data(self, **kwargs)
        content['participant'],content['active'] = get_user_status(
            self.request,self.kwargs.get('slug'))
        return content
    def post(self,request,**kwargs):
        user = request.user
        if not user.is_authenticated():
            raise Http404
        self.object = self.get_object(self.get_queryset())
        participant,active = get_user_status(request,self.kwargs.get('slug'))
        
        if active and not participant.opted_out:
            participant.opted_out = True
            participant.enrolled = False
            participant.save()
        return self.get(request,**kwargs)

class SwitchReportView(SwitchDetailView):
    template_name = 'leaner/switch-report.html'
    
    def get_context_data(self, **kwargs):
        kwargs['goal_types'] = GoalType.objects.filter(switch=self.object) 
        kwargs['switch_key'] = self.kwargs.get('slug')
        kwargs['group_users'] = Participant.objects.filter(enrolled=True,
            switch__key=self.kwargs.get('slug')).count()
        kwargs['non_group_users'] = User.objects.all().count() - kwargs['group_users']
        return SwitchDetailView.get_context_data(self, **kwargs)

    @method_decorator(user_passes_test(lambda u: u.is_staff))
    def get(self, request, **kwargs):
        return SwitchDetailView.get(self, request, **kwargs)

class TestSwitchPageView(BaseSwitchDetailView):
    template_name = 'leaner/test-switch-page.html'
    
    def get_context_data(self, **kwargs):
        content = BaseSwitchDetailView.get_context_data(self, **kwargs)
        content['participant'],content['active'] = get_user_status(self.request,
            self.kwargs.get('slug'))
        return content
    
    def get(self, request, **kwargs):
        if not LEANER_DEBUG:
            raise Http404
        return BaseSwitchDetailView.get(self, request, **kwargs)
    
class TestSwitchGoalRecordView(DetailView):
    model = GoalType
    template_name = 'leaner/test-switch-page-goalrecord.html'
    
    def get(self, request, **kwargs):
        if not LEANER_DEBUG:
            raise Http404
        return DetailView.get(self, request, **kwargs)
    
    def get_context_data(self, **kwargs):
        context = DetailView.get_context_data(self, **kwargs)
        switch_key = self.kwargs.get('key')
        goal_type_slug = self.kwargs.get('slug')
        try:
            context['switch'] = Switch.objects.get(key=switch_key)
        except Switch.DoesNotExist:
            raise Http404
        context['goal_record'] = record(switch_key, goal_type_slug, self.request)
        return context 