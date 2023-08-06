'''
Created on May 15, 2012

@author: brian
'''
from django.conf import settings
from django.http import HttpResponseRedirect

from leaner.goalrecord.utils import get_user_status

LEANER_REMOTE_SWITCH_KEY = getattr(settings, 'LEANER_REMOTE_SWITCH_KEY',None)
LEANER_TEST_SITE_URL = getattr(settings,'LEANER_TEST_SITE_URL',None)
LEANER_REMOTE_PROTOCOL = getattr(settings,'LEANER_REMOTE_PROTOCOL','http://')

class RemoteSwitchMiddleware(object):
    '''
    Middleware that should only be used if you have a gigantic switch 
    that needs to be tested on a different sub-domain. If the users 
    aren't in the test group they will remain on your main production 
    site and if not they will be redirected to the test site. Make sure
    both sites share the same SECRET_KEY, SESSION_COOKIE_DOMAIN,
    and the user information is in the same DB. This middleware can 
    only be used for one switch at a time (sorry).
    '''
    
    def process_request(self,request):
        if not request.user.is_authenticated():
            return None
        participant, active = get_user_status(request,LEANER_REMOTE_SWITCH_KEY)
        host = request.META.get('HTTP_HOST') or request.META.get('SERVER_NAME')
        
        if active == True and host != LEANER_TEST_SITE_URL:
            return HttpResponseRedirect('{0}{1}{2}'.format(
                LEANER_REMOTE_PROTOCOL,LEANER_TEST_SITE_URL,
                request.path_info))
        return None