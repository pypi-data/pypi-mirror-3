'''
Created on Apr 30, 2012

@author: brian
'''
from django.conf.urls.defaults import *
from views import *
urlpatterns = patterns('',
    url(r'^feature/(?P<slug>[-\w]+)/$', SwitchDetailView.as_view() , name="leaner_switch_detail"),
    url(r'^(?P<slug>[-\w]+)/$', SwitchReportView.as_view() , name="leaner_switch_report"),
    url(r'^test/(?P<slug>[-\w]+)/$', TestSwitchPageView.as_view() , name="test_leaner_switch"),
    url(r'^test/(?P<key>[-\w]+)/(?P<slug>[-\w]+)/$', TestSwitchGoalRecordView.as_view() , name="test_leaner_goalrecord"), 
)