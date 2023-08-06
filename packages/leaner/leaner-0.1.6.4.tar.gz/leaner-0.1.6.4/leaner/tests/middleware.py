'''
Created on May 16, 2012

@author: brian
'''

from ..utils import LeanerTestCase
from django.conf import settings

DEFAULT_MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
)

class MiddlewareTestCase(LeanerTestCase):
    '''
    Test for RemoteSwitchMiddleware. Please make sure you have the 
    correct settings to run these tests.
    '''
    def setUp(self):
        self.switch =self.create_switch('crazy-horse',
            """{"auth.user": {"percent": [["i","0-50"]]}}""",
            'Crazy Horse Switch',
            'This is a test switch.')
        self.users = [self.create_user('test_user{0}'.format(i),
            't{0}@example.com'.format(i)) for i in range(100)]
        self.in_user = 1
        self.out_user = 51
        self.user = self.users[1]
        self.not_user = self.users[51]
        settings.LEANER_REMOTE_SWITCH_KEY = 'crazy-horse'
        settings.LEANER_TEST_SITE_URL = 'www.dnsly.net'
        settings.MIDDLEWARE_CLASSES += (
            'leaner.middleware.RemoteSwitchMiddleware',
                           )
        
    def test_redirect_test_group(self):
        self.client.login(username=self.user.username,password='test')
        path = self.reverse('test_leaner_switch',args=[self.switch.key])
        response = self.client.get(path)
        test_url = self.reverse('test_leaner_switch', [self.switch.key])
        self.assertRedirects(response,
            'http://{0}{1}'.format(settings.LEANER_TEST_SITE_URL,test_url),
            302, 302)
        
    def test_not_redirect_control_group(self):
        self.client.login(username=self.not_user.username,password='test')
        path = self.reverse('test_leaner_switch',args=[self.switch.key])
        response = self.client.get(path)
        self.assertEqual(response.status_code, 200)
        
    def tearDown(self):
        settings.MIDDLEWARE_CLASSES = DEFAULT_MIDDLEWARE_CLASSES