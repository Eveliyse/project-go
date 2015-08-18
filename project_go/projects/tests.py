from django.test import TestCase
from django.contrib.auth.models import User
from .models import Project, Reward, Status, Pledge
from django.core.urlresolvers import reverse

class BaseProjectsTestCase(TestCase):
    
    fixtures = ['users_views_testdata.json', 'auth_views_testdata.json']
        
    def login(self, uname='admin', password='admin'):
        res = self.client.post(reverse('users:login'), {'username': uname, 'password': password})
        self.assertEqual(res.status_code, 302)
        self.assertRedirects(res, reverse('users:index'))
        self.assertIn('_auth_user_id', self.client.session)
        self.user = User.objects.get(username=uname)

class ProjectsIndexViewTestCase(BaseProjectsTestCase):
    def test_index(self):
        res = self.client.get(reverse('projects:index'))
        self.assertEqual(res.status_code, 200)
