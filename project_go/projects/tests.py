from django.test import TestCase
from django.contrib.auth.models import User
from .models import Project, Reward, Pledge
from django.core.urlresolvers import reverse

class BaseProjectsTestCase(TestCase):
    #load test data
    fixtures=['projects_views_testdata.json', 'auth_views_testdata.json']
    
    all_projects=Project.objects.all()
    all_pledges=Pledge.objects.all()
    all_rewards=Reward.objects.all()    
        
    def login(self, uname='admin', password='admin'):
        res=self.client.post(reverse('users:login'), {'username': uname, 'password': password})
        self.assertEqual(res.status_code, 302)
        self.assertRedirects(res, reverse('users:index'))
        self.assertIn('_auth_user_id', self.client.session)
        self.user=User.objects.get(username=uname)
        
        #create sets related to user
        self.user_projects=Project.objects.filter(owner=self.user)
        self.user_pledges=Pledge.objects.filter(project__id__in=self.user_projects)
        self.user_rewards=Reward.objects.filter(project__id__in=self.user_projects)
        
        #create sets not related to user
        self.not_user_projects=Project.objects.exclude(owner=self.user)
        self.not_user_pledges=Pledge.objects.exclude(project__id__in=self.user_projects)
        self.not_user_rewards=Reward.objects.exclude(project__id__in=self.user_projects)
        
class ProjectsIndexViewTestCase(BaseProjectsTestCase):
    def test_index(self):
        #not logged in
        res=self.client.get(reverse('projects:index'))
        self.assertEqual(res.status_code, 302)
        self.assertRedirects(res, reverse('users:login') + "?next=%s" % reverse('projects:index'))  
        
        #logged in
        self.login()
        res=self.client.get(reverse('projects:index'))
        self.assertEqual(res.status_code, 200)            
        
class ProjectsManageViewTestCase(BaseProjectsTestCase):
    def test_manage(self):
        #not logged in
        res=self.client.get(reverse('projects:manage'))
        self.assertEqual(res.status_code, 302)
        self.assertRedirects(res, reverse('users:login') + "?next=%s" % reverse('projects:manage'))
        
        #logged in
        self.login()
        res=self.client.get(reverse('projects:manage'))
        self.assertEqual(res.status_code, 200)    
        
class ProjectsCreateViewTestCase(BaseProjectsTestCase):
    def test_create(self):
        #not logged in
        res=self.client.get(reverse('projects:create'))
        self.assertEqual(res.status_code, 302)
        self.assertRedirects(res, reverse('users:login') + "?next=%s" % reverse('projects:create'))
        
        #logged in
        self.login()
        res=self.client.get(reverse('projects:create'))
        self.assertEqual(res.status_code, 200)
        self.assertIsNotNone(res.context['form'])
        
class ProjectsEditViewTestCase(BaseProjectsTestCase):
    def test_edit_project_id(self):
        #Should I test '@login_required'?
        self.login()

        #edit own project
        res=self.client.get(reverse('projects:edit', kwargs={'project_id':self.user_projects[0].id}))
        self.assertEqual(res.status_code, 200)   
        self.assertIsNotNone(res.context['form'])
        self.assertIsNotNone(res.context['pledges'])
        self.assertIsNotNone(res.context['project'])
        
        #edit not own project
        res=self.client.get(reverse('projects:edit', kwargs={'project_id':self.not_user_projects[0].id}))
        self.assertEqual(res.status_code, 302)           
        self.assertRedirects(res, reverse('projects:manage'))
        
        #edit nonexistent project
        res=self.client.get(reverse('projects:edit', kwargs={'project_id':9876543210}))
        self.assertEqual(res.status_code, 404)
        
class ProjectsPledgeRewardsViewTestCase(BaseProjectsTestCase):
    
    def test_add_pledgerewards_id(self):
        #Should I test '@login_required'?
        self.login()
        
        #add pledge/rewards to own project
        res=self.client.get(reverse('projects:pledgerewards', kwargs={'project_id':self.user_projects[0].id}))
        self.assertEqual(res.status_code, 200)   
        self.assertIsNotNone(res.context['form2'])
        self.assertIsNotNone(res.context['form3'])
        self.assertIsNotNone(res.context['pledges'])
        self.assertIsNotNone(res.context['rewards'])
        self.assertIsNotNone(res.context['project'])
        
        #add pledge/rewards to not own project
        res=self.client.get(reverse('projects:pledgerewards', kwargs={'project_id':self.not_user_projects[0].id}))
        self.assertEqual(res.status_code, 302)           
        self.assertRedirects(res, reverse('projects:manage'))
        
        #add pledge/rewards to nonexistent project
        res=self.client.get(reverse('projects:pledgerewards', kwargs={'project_id':9876543210}))
        self.assertEqual(res.status_code, 404)        

    def test_edit_pledge_id(self):
        #Should I test '@login_required'?        
        self.login()
        
        #edit pledge for own project
        res=self.client.get(reverse('projects:pledge', kwargs={'project_id':self.user_pledges[0].project.id,
                                                                 'P_R_id':self.user_pledges[0].id}))
        self.assertEqual(res.status_code, 200)   
        self.assertIsNotNone(res.context['form2'])
        self.assertIsNotNone(res.context['form3'])
        self.assertIsNotNone(res.context['mode'])
        self.assertIsNotNone(res.context['instance'])
        self.assertIsNotNone(res.context['pledges'])
        self.assertIsNotNone(res.context['rewards'])
        self.assertIsNotNone(res.context['project'])

        #edit pledge for not own project
        res=self.client.get(reverse('projects:pledge', kwargs={'project_id':self.not_user_pledges[0].project.id,
                                                                 'P_R_id':self.not_user_pledges[0].id}))
        self.assertEqual(res.status_code, 302)   
        self.assertRedirects(res, reverse('projects:manage'))
    
        #edit nonexistnet pledge
        res=self.client.get(reverse('projects:pledge', kwargs={'project_id':self.user_pledges[0].project.id,
                                                                 'P_R_id':9876543210}))
        self.assertEqual(res.status_code, 404)
        
    def test_edit_reward_id(self):
        #Should I test '@login_required'? 
        self.login()
        
        #edit reward for own project
        res=self.client.get(reverse('projects:reward', kwargs={'project_id':self.user_rewards[0].project.id,
                                                                 'P_R_id':self.user_rewards[0].id}))
        self.assertEqual(res.status_code, 200)   
        self.assertIsNotNone(res.context['form2'])
        self.assertIsNotNone(res.context['form3'])
        self.assertIsNotNone(res.context['mode'])
        self.assertIsNotNone(res.context['instance'])
        self.assertIsNotNone(res.context['pledges'])
        self.assertIsNotNone(res.context['rewards'])
        self.assertIsNotNone(res.context['project'])

        #edit reward for not own project
        res=self.client.get(reverse('projects:reward', kwargs={'project_id':self.not_user_rewards[0].project.id,
                                                                 'P_R_id':self.not_user_rewards[0].id}))
        self.assertEqual(res.status_code, 302)   
        self.assertRedirects(res, reverse('projects:manage'))
    
        #edit nonexistent reward
        res=self.client.get(reverse('projects:pledge', kwargs={'project_id':self.user_rewards[0].project.id,
                                                                 'P_R_id':9876543210}))
        self.assertEqual(res.status_code, 404)

class ProjectsPledgeRewardsDeleteViewTestCase(BaseProjectsTestCase):
    def test_pledge_delete_id(self):
        #Should I test '@login_required'? 
        self.login()
        
        #delete pledge for own project
        res=self.client.get(reverse('projects:deletepledge', kwargs={'project_id':self.user_pledges[0].project.id,
                                                                       'P_R_id':self.user_pledges[0].id}))
        self.assertEqual(res.status_code, 302)  
        self.assertRedirects(res, reverse('projects:pledgerewards', kwargs={'project_id':self.user_pledges[0].project.id}))
        
        #delete pledge for not own project
        res=self.client.get(reverse('projects:deletepledge', kwargs={'project_id':self.not_user_pledges[0].project.id,
                                                                       'P_R_id':self.not_user_pledges[0].id}))
        self.assertEqual(res.status_code, 302)  
        self.assertRedirects(res, reverse('projects:manage'))        
        
        #delete nonexistent pledge
        res=self.client.get(reverse('projects:deletepledge', kwargs={'project_id':self.user_pledges[0].project.id,
                                                                       'P_R_id':9876543210}))
        self.assertEqual(res.status_code, 404)          
        
    def test_pledge_delete_id(self):
        #Should I test '@login_required'? 
        self.login()    
        
        #delete reward for own project
        res=self.client.get(reverse('projects:deletereward',kwargs={'project_id':self.user_rewards[0].project.id,
                                                                       'P_R_id':self.user_rewards[0].id}))
        self.assertEqual(res.status_code, 302)
        self.assertRedirects(res, reverse('projects:pledgerewards', kwargs={'project_id':self.user_rewards[0].project.id}))
        
        #delete reward for not own project
        res=self.client.get(reverse('projects:deletereward', kwargs={'project_id':self.not_user_rewards[0].project.id,
                                                                       'P_R_id':self.not_user_rewards[0].id}))
        self.assertEqual(res.status_code, 302)  
        self.assertRedirects(res, reverse('projects:manage'))                

        #delete nonexistent reward
        res=self.client.get(reverse('projects:deletereward', kwargs={'project_id':self.user_rewards[0].project.id,
                                                                       'P_R_id':9876543210}))
        self.assertEqual(res.status_code, 404)
        
class ProjectsDetailsViewTestCase(BaseProjectsTestCase):
    def test_details(self):
        #not logged in
        res=self.client.get(reverse('projects:details'))
        self.assertEqual(res.status_code, 200)
    
        #logged in
        self.login()
        res=self.client.get(reverse('projects:details'))
        self.assertEqual(res.status_code, 200)   