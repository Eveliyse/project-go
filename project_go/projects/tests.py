from django.test import TestCase
from django.contrib.auth.models import User
from .models import Project, Reward, Status, Pledge
from django.core.urlresolvers import reverse

class BaseProjectsTestCase(TestCase):
    
    fixtures = ['projects_views_testdata.json', 'auth_views_testdata.json']
        
    def login(self, uname='admin', password='admin'):
        res = self.client.post(reverse('users:login'), {'username': uname, 'password': password})
        self.assertEqual(res.status_code, 302)
        self.assertRedirects(res, reverse('users:index'))
        self.assertIn('_auth_user_id', self.client.session)
        self.user = User.objects.get(username=uname)

class ProjectsIndexViewTestCase(BaseProjectsTestCase):
    def test_index(self):
        res = self.client.get(reverse('projects:index'))
        self.assertEqual(res.status_code, 302)
        self.assertRedirects(res, reverse('users:login') + "?next=%s" % reverse('projects:index'))  
        
        self.login()
        res = self.client.get(reverse('projects:index'))
        self.assertEqual(res.status_code, 200)            
        
class ProjectsManageViewTestCase(BaseProjectsTestCase):
    def test_manage(self):
        res = self.client.get(reverse('projects:manage'))
        self.assertEqual(res.status_code, 302)
        self.assertRedirects(res, reverse('users:login') + "?next=%s" % reverse('projects:manage'))
        
        self.login()
        res = self.client.get(reverse('projects:manage'))
        self.assertEqual(res.status_code, 200)    
        
class ProjectsCreateViewTestCase(BaseProjectsTestCase):
    def test_create(self):
        res = self.client.get(reverse('projects:create'))
        self.assertEqual(res.status_code, 302)
        self.assertRedirects(res, reverse('users:login') + "?next=%s" % reverse('projects:create'))
        
        self.login()
        res = self.client.get(reverse('projects:create'))
        self.assertEqual(res.status_code, 200)
        self.assertIsNotNone(res.context['form'])
        
class ProjectsEditViewTestCase(BaseProjectsTestCase):
    projects = Project.objects.all()    
    
    def test_edit_project_id(self):
        self.login()
        res = self.client.get(reverse('projects:edit', kwargs={'project_id':self.projects[1].id}))
        self.assertEqual(res.status_code, 200)   
        self.assertIsNotNone(res.context['form'])
        self.assertIsNotNone(res.context['pledges'])
        self.assertIsNotNone(res.context['project'])
        
        res = self.client.get(reverse('projects:edit', kwargs={'project_id':987654321}))
        self.assertEqual(res.status_code, 404)        
        
class ProjectsPledgeRewardsViewTestCase(BaseProjectsTestCase):
    projects = Project.objects.all()     
    
    def test_pledgerewards_id(self):
        self.login()
        res = self.client.get(reverse('projects:pledgerewards', kwargs={'project_id':self.projects[1].id}))
        self.assertEqual(res.status_code, 200)   
        self.assertIsNotNone(res.context['form2'])
        self.assertIsNotNone(res.context['form3'])
        self.assertIsNotNone(res.context['pledges'])
        self.assertIsNotNone(res.context['rewards'])
        self.assertIsNotNone(res.context['project'])
        
        res = self.client.get(reverse('projects:pledgerewards', kwargs={'project_id':987654321}))
        self.assertEqual(res.status_code, 404)        


class ProjectsDetailsViewTestCase(BaseProjectsTestCase):
    def test_details(self):
        res = self.client.get(reverse('projects:details'))
        self.assertEqual(res.status_code, 200)
    
        self.login()
        res = self.client.get(reverse('projects:details'))
        self.assertEqual(res.status_code, 200)   