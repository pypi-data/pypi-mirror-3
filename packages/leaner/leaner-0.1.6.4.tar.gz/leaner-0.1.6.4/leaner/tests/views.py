'''
Created on Apr 26, 2012

@author: brian
'''
from leaner.utils import LeanerTestCase
from ..models import GoalType
__all__ = ('SwitchDetailViewTestCase',)

class SwitchDetailViewTestCase(LeanerTestCase):
    
    def setUp(self):
        self.switch =self.create_switch('crazy-horse',
            """{"auth.user": {"percent": [["i","0-50"]]}}""",
            'Crazy Horse Switch',
            'This is a test switch.')
        self.goal_type = GoalType.objects.create(switch=self.switch,
            name='Test Goal Type',slug='test-goal-type')
        self.users = [self.create_user('test_user{0}'.format(i),'t{0}@example.com'.format(i)) for i in range(100)]
        self.in_user = 1
        self.out_user = 51
        self.user = self.users[1]
        self.not_user = self.users[51]
        
    def test_in_group(self):
        self.client.login(username=self.user.username,
            password=self.user_password)
        
        response = self.client.get(self.reverse('test_leaner_switch',
            args=[self.switch.key]))
        self.assertContains(response,'test_user1',1,200)
        self.assertContains(response, 'This is a test switch', 1, 200)
        self.assertContains(response, 'Crazy Horse Switch', 4, 200)
        self.assertContains(response,
            'test_user{0} you are in this test group.'.format(self.in_user),
            1, 200)
        
    def test_not_in_group(self):
        self.client.login(username=self.not_user.username,
                          password=self.user_password)
        response = self.client.get(
            self.reverse('test_leaner_switch',args=[self.switch.key]))
        self.assertContains(response,
            'test_user{0} you are not in this test group.'.format(self.out_user),
            1, 200)
        
    def test_opt_out(self):
        self.client.login(username=self.user.username,
                          password=self.user_password)
        
        response = self.client.get(
            self.reverse('test_leaner_switch',args=[self.switch.key]))
        
        self.assertContains(response,
            'test_user{0} you are in this test group.'.format(self.in_user),
            1, 200)
        
        response = self.client.get(self.reverse('leaner_switch_detail',
            args=[self.switch.key]))
        
        self.assertContains(response, 'Opt-out of this Feature Group', 1, 200)
        
        response = self.client.post(self.reverse('leaner_switch_detail',
            args=[self.switch.key]))
        
        self.assertNotContains(response, 'Opt-out of this Feature Group', 200)
        
    def test_multiple_goal_records(self):
        self.client.login(username=self.user.username,
                          password=self.user_password)
        response = self.client.get(self.reverse('test_leaner_goalrecord',
            args=[self.switch.key,self.goal_type.slug]))
        trigger_txt = 'test_user1 you did trigger'
        not_trigger_txt = 'test_user1 you did not trigger'
        
        self.assertContains(response, trigger_txt, 1, 200)
        
        response = self.client.get(self.reverse('test_leaner_goalrecord',
            args=[self.switch.key,self.goal_type.slug]))
        
        self.assertContains(response, not_trigger_txt,1, 200)
        
    def test_goal_records_not_logged_in(self):
        response = self.client.get(self.reverse('test_leaner_goalrecord',
            args=[self.switch.key,self.goal_type.slug]))
        not_trigger_txt = "You cannot trigger a goal record if you're not logged in."
        self.assertContains(response, not_trigger_txt, 1, 200)
        