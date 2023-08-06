'''
Created on May 29, 2012

@author: brian
'''
from django.test.client import RequestFactory
from django.core.urlresolvers import reverse
from django.contrib.sessions.backends.db import SessionStore
from django.contrib.auth.models import User

from ..goalrecord.utils import get_user_status
from ..utils import LeanerTestCase

class UserStatusTestCase(LeanerTestCase):
    
    def setUp(self):
        self.switch =self.create_switch('crazy-horse',
            """{"auth.user": {"percent": [["i","0-50"]]}}""",
            'Crazy Horse Switch',
            'This is a test switch.')
        
        self.factory = RequestFactory()
        self.request = self.factory.get(
            self.reverse('test_leaner_switch',args=[self.switch.key]))
        self.users = [self.create_user('test_user{0}'.format(i),'t{0}@example.com'.format(i)) for i in range(60)]
        self.in_user = 1
        self.out_user = 51
        self.user = self.users[1]
        self.not_user = self.users[51]
        
    def test_active(self):
        
        
        session = SessionStore()
        session.save()
        self.request.session = session
        self.request.user = self.user
        
        participant,active = get_user_status(self.request, self.switch.key)
        self.assertTrue(active == True,
            'Participant is not active when they should be')
    
    def test_inactive(self):
        session = SessionStore()
        session.save()
        self.request.session = session
        self.request.user = self.not_user
        participant,active = get_user_status(self.request, self.switch.key)
        self.assertTrue(active == False,
            'Participant is not active when they should be')
        