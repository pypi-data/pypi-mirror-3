'''
Created on Mar 2, 2012

@author: brian
'''
import hashlib

from django.conf import settings
from django.test import TestCase
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse

from gargoyle.models import Switch

__all__ = ('get_key','LeanerTestCase')
     
def get_key(user,switch_key):
    return hashlib.sha256('{0}{1}{2}'.format(settings.SECRET_KEY,
        user.id,switch_key)).hexdigest()
        
class LeanerTestCase(TestCase):
    user_password = 'test'
    
    def create_switch(self,key,value,label=None,description=None,status=2):
        return Switch.objects.create(key=key,value=value,
            label=label,description=description,status=status)
        
    def reverse(self,viewname, args=None, kwargs=None):
        return reverse(viewname,args=args, kwargs=kwargs)
    
    def create_user(self,username='testuser',
                    email='test@example.com'):
        return User.objects.create_user(username, email, self.user_password)   