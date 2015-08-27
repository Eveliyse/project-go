from django.test import TestCase
from django.contrib.auth.models import User
from .models import Project, Reward, Pledge, Category, Status
from django.core.urlresolvers import reverse

class BaseProjectsTestCase(TestCase):
    #load test data
    fixtures=['projects_views_testdata.json', 'auth_views_testdata.json']
    
    all_projects=Project.objects.all()
    all_pledges=Pledge.objects.all()
    all_rewards=Reward.objects.all()    
    
    new_status = Status.objects.get(status = "New")
    open_status = Status.objects.get(status = "Open")
    closed_status = Status.objects.get(status = "Closed")    

    def login(self, uname='admin', password='admin'):
        res=self.client.post(reverse('users:login'), {'username': uname, 'password': password})
        self.assertEqual(res.status_code, 302)
        #self.assertRedirects(res, reverse('users:index'))
        self.assertIn('_auth_user_id', self.client.session)
        self.user=User.objects.get(username=uname)
        
        #create sets related to user
        self.user_projects=Project.objects.filter(owner=self.user)
        self.user_pledges=Pledge.objects.filter(project__id__in=self.user_projects)
        self.user_rewards=Reward.objects.filter(project__id__in=self.user_projects)
        
        self.new_projects = self.user_projects.filter(status = self.new_status)
        self.open_projects = self.user_projects.filter(status = self.open_status)
        self.closed_projects = self.user_projects.filter(status = self.closed_status)        
        
        
        #create sets not related to user
        self.not_user_projects=Project.objects.exclude(owner=self.user)
        self.not_user_pledges=Pledge.objects.exclude(project__id__in=self.user_projects)
        self.not_user_rewards=Reward.objects.exclude(project__id__in=self.user_projects)
        
        
class ProjectsIndexViewTestCase(BaseProjectsTestCase):
    def test_index(self):
        #not logged in
        res=self.client.get(reverse('projects:index'))
        self.assertEqual(res.status_code, 200)
        
        #logged in
        self.login()
        res=self.client.get(reverse('projects:index'))
        self.assertEqual(res.status_code, 200)            
        
class ProjectsManageViewTestCase(BaseProjectsTestCase):
    def test_manage_projects(self):
        #not logged in
        res=self.client.get(reverse('projects:manage'))
        self.assertEqual(res.status_code, 302)
        self.assertRedirects(res, reverse('users:login') + "?next=%s" % reverse('projects:manage'))
        
        #logged in
        self.login()
        res=self.client.get(reverse('projects:manage'))
        self.assertEqual(res.status_code, 200)    
        
class ProjectsCreateViewTestCase(BaseProjectsTestCase):
    def test_create_project(self):
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
    def test_edit_project(self):
        #Should I test '@login_required'?
        self.login()

        #edit own project
        res=self.client.get(reverse('projects:edit', kwargs={'project_id':self.new_projects[0].id}))
        self.assertEqual(res.status_code, 200)   
        self.assertIsNotNone(res.context['form'])
        self.assertIsNotNone(res.context['pledges'])
        self.assertIsNotNone(res.context['project'])
        
        res=self.client.get(reverse('projects:edit', kwargs={'project_id':self.open_projects[0].id}))
        self.assertEqual(res.status_code, 302)           

        res=self.client.get(reverse('projects:edit', kwargs={'project_id':self.closed_projects[0].id}))
        self.assertEqual(res.status_code, 302)           
    
        #edit not own project
        res=self.client.get(reverse('projects:edit', kwargs={'project_id':self.not_user_projects[0].id}))
        self.assertEqual(res.status_code, 302)           
        self.assertRedirects(res, reverse('projects:manage'))
        
        #edit nonexistent project
        res=self.client.get(reverse('projects:edit', kwargs={'project_id':9876543210}))
        self.assertEqual(res.status_code, 404)
        
class ProjectsPledgeRewardsViewTestCase(BaseProjectsTestCase):
    def test_add_pledgerewards(self):
        #Should I test '@login_required'?
        self.login()
        
        #add pledge/rewards to own project
        res=self.client.get(reverse('projects:pledgerewards', kwargs={'project_id':self.new_projects[0].id}))
        self.assertEqual(res.status_code, 200)   
        self.assertIsNotNone(res.context['form2'])
        self.assertIsNotNone(res.context['form3'])
        self.assertIsNotNone(res.context['pledges'])
        self.assertIsNotNone(res.context['rewards'])
        self.assertIsNotNone(res.context['project'])
        
        res=self.client.get(reverse('projects:pledgerewards', kwargs={'project_id':self.open_projects[0].id}))
        self.assertEqual(res.status_code, 302)
        
        res=self.client.get(reverse('projects:pledgerewards', kwargs={'project_id':self.closed_projects[0].id}))
        self.assertEqual(res.status_code, 302)        
        
        #add pledge/rewards to not own project
        res=self.client.get(reverse('projects:pledgerewards', kwargs={'project_id':self.not_user_projects[0].id}))
        self.assertEqual(res.status_code, 302)           
        self.assertRedirects(res, reverse('projects:manage'))
        
        #add pledge/rewards to nonexistent project
        res=self.client.get(reverse('projects:pledgerewards', kwargs={'project_id':9876543210}))
        self.assertEqual(res.status_code, 404)        

    def test_edit_pledgereward(self):
        #Should I test '@login_required'?        
        self.login()
        
        #edit pledge for own project
        res=self.client.get(reverse('projects:pledge', kwargs={'project_id':self.new_projects[0].id,
                                                                 'P_R_id':self.new_projects[0].project_pledges.all()[0].id}))
        self.assertEqual(res.status_code, 200)   
        self.assertIsNotNone(res.context['form2'])
        self.assertIsNotNone(res.context['form3'])
        self.assertIsNotNone(res.context['mode'])
        self.assertIsNotNone(res.context['instance'])
        self.assertIsNotNone(res.context['pledges'])
        self.assertIsNotNone(res.context['rewards'])
        self.assertIsNotNone(res.context['project'])
        
        res=self.client.get(reverse('projects:pledge', kwargs={'project_id':self.open_projects[0].id,
                                                               'P_R_id':self.open_projects[0].project_pledges.all()[0].id}))
        self.assertEqual(res.status_code, 302)

        res=self.client.get(reverse('projects:pledge', kwargs={'project_id':self.closed_projects[0].id,
                                                               'P_R_id':self.closed_projects[0].project_pledges.all()[0].id}))
        self.assertEqual(res.status_code, 302)

        #edit pledge for not own project
        res=self.client.get(reverse('projects:pledge', kwargs={'project_id':self.not_user_pledges[0].project.id,
                                                                 'P_R_id':self.not_user_pledges[0].id}))
        self.assertEqual(res.status_code, 302)   
        self.assertRedirects(res, reverse('projects:manage'))
    
        #edit nonexistnet pledge
        res=self.client.get(reverse('projects:pledge', kwargs={'project_id':self.new_projects[0].id,
                                                                 'P_R_id':9876543210}))
        self.assertEqual(res.status_code, 404)
        
    def test_edit_reward(self):
        #Should I test '@login_required'? 
        self.login()
        
        #edit reward for own project
        res=self.client.get(reverse('projects:reward', kwargs={'project_id':self.new_projects[0].id,
                                                               'P_R_id':self.new_projects[0].project_pledges.all()[0].rewards.all()[0].id}))
        self.assertEqual(res.status_code, 200)   
        self.assertIsNotNone(res.context['form2'])
        self.assertIsNotNone(res.context['form3'])
        self.assertIsNotNone(res.context['mode'])
        self.assertIsNotNone(res.context['instance'])
        self.assertIsNotNone(res.context['pledges'])
        self.assertIsNotNone(res.context['rewards'])
        self.assertIsNotNone(res.context['project'])

        res=self.client.get(reverse('projects:reward', kwargs={'project_id':self.open_projects[0].id,
                                                               'P_R_id':self.open_projects[0].project_pledges.all()[0].rewards.all()[0].id}))
        self.assertEqual(res.status_code, 302)   
        
        res=self.client.get(reverse('projects:reward', kwargs={'project_id':self.closed_projects[0].id,
                                                               'P_R_id':self.closed_projects[0].project_pledges.all()[0].rewards.all()[0].id}))
        self.assertEqual(res.status_code, 302)

        #edit reward for not own project
        res=self.client.get(reverse('projects:reward', kwargs={'project_id':self.not_user_rewards[0].project.id,
                                                                 'P_R_id':self.not_user_rewards[0].id}))
        self.assertEqual(res.status_code, 302)   
        self.assertRedirects(res, reverse('projects:manage'))
    
        #edit nonexistent reward
        res=self.client.get(reverse('projects:reward', kwargs={'project_id':self.new_projects[0].id,
                                                                 'P_R_id':9876543210}))
        self.assertEqual(res.status_code, 404)

class ProjectsPledgeRewardsDeleteViewTestCase(BaseProjectsTestCase):
    def test_delete_pledgereward(self):
        #Should I test '@login_required'? 
        self.login()
        
        #delete pledge for own project
        res=self.client.get(reverse('projects:delete_pledge', kwargs={'project_id':self.new_projects[0].id,
                                                                       'P_R_id':self.new_projects[0].project_pledges.all()[0].id}))
        self.assertEqual(res.status_code, 302)  
        self.assertRedirects(res, reverse('projects:pledgerewards', kwargs={'project_id':self.new_projects[0].id}))
        
        #delete pledge for not own project
        res=self.client.get(reverse('projects:delete_pledge', kwargs={'project_id':self.not_user_pledges[0].project.id,
                                                                       'P_R_id':self.not_user_pledges[0].id}))
        self.assertEqual(res.status_code, 302)  
        self.assertRedirects(res, reverse('projects:manage'))        
        
        #delete nonexistent pledge
        res=self.client.get(reverse('projects:delete_pledge', kwargs={'project_id':self.user_pledges[0].project.id,
                                                                       'P_R_id':9876543210}))
        self.assertEqual(res.status_code, 404)          
        
    def test_delete_reward(self):
        #Should I test '@login_required'? 
        self.login()    
        
        #delete reward for own project
        res=self.client.get(reverse('projects:delete_reward',kwargs={'project_id':self.new_projects[0].id,
                                                                       'P_R_id':self.new_projects[0].project_pledges.all()[0].rewards.all()[0].id}))
        self.assertEqual(res.status_code, 302)
        self.assertRedirects(res, reverse('projects:pledgerewards', kwargs={'project_id':self.new_projects[0].id}))
        
        #delete reward for not own project
        res=self.client.get(reverse('projects:delete_reward', kwargs={'project_id':self.not_user_rewards[0].project.id,
                                                                       'P_R_id':self.not_user_rewards[0].id}))
        self.assertEqual(res.status_code, 302)  
        self.assertRedirects(res, reverse('projects:manage'))                

        #delete nonexistent reward
        res=self.client.get(reverse('projects:delete_reward', kwargs={'project_id':self.user_rewards[0].project.id,
                                                                       'P_R_id':9876543210}))
        self.assertEqual(res.status_code, 404)
        
class ProjectsDetailsViewTestCase(BaseProjectsTestCase):
    def test_view_project_details(self):
        #not logged in
        res=self.client.get(reverse('projects:details', kwargs={'project_id':self.all_projects[0].id}))
        self.assertEqual(res.status_code, 200)
        
        res=self.client.get(reverse('projects:details', kwargs={'project_id':9876543210}))
        self.assertEqual(res.status_code,404)        
        
        #logged in
        self.login()
        
        #details for own project
        res=self.client.get(reverse('projects:details', kwargs={'project_id':self.user_projects[0].id}))
        self.assertEqual(res.status_code, 200)
        
        #details for not own project
        self.login()
        res=self.client.get(reverse('projects:details', kwargs={'project_id':self.not_user_projects[0].id}))
        self.assertEqual(res.status_code, 200)        
    
        #details for nonexistent project
        res=self.client.get(reverse('projects:details', kwargs={'project_id':9876543210}))
        self.assertEqual(res.status_code,404)   
        
class ProjectsListViewTestCase(BaseProjectsTestCase):
    all_categories = Category.objects.all()
    
    def test_project_categories(self):
        #categories
        res=self.client.get(reverse('projects:category', kwargs={'category_id':self.all_categories[0].id}))
        self.assertEqual(res.status_code, 200)
        
        res=self.client.get(reverse('projects:category', kwargs={'category_id':9876543210}))
        self.assertEqual(res.status_code,404)    
        
    def test_project_search(self):
        #search
        res=self.client.get(reverse('projects:search'))
        self.assertEqual(res.status_code, 200)

        res=self.client.get("%s?search_term=%s" % (reverse('projects:search'), self.all_projects[0].title))
        self.assertEqual(res.status_code, 200)        
    
        res=self.client.get("%s?search_term=kjghskerhbgserugnserknguybserkgu" % reverse('projects:search'))
        self.assertEqual(res.status_code,200)   