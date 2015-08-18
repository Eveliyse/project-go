from django.test import TestCase
from django.contrib.auth.models import User
from .models import Member, Address, Country, Gender
from django.core.urlresolvers import reverse

class BaseUsersTestCase(TestCase):
    
    fixtures = ['users_views_testdata.json', 'auth_views_testdata.json']
        
    def login(self, uname='admin', password='admin'):
        res = self.client.post(reverse('users:login'), {'username': uname, 'password': password})
        self.assertEqual(res.status_code, 302)
        self.assertRedirects(res, reverse('users:index'))
        self.assertIn('_auth_user_id', self.client.session)
        self.user = User.objects.get(username=uname)

class UsersIndexViewTestCase(BaseUsersTestCase):
    def test_index(self):
        res = self.client.get(reverse('users:index'))
        self.assertEqual(res.status_code, 200)

class UsersProfileViewTestCase(BaseUsersTestCase):        
    def test_profile(self):
        res = self.client.get(reverse('users:userprofile'))
        self.assertEqual(res.status_code, 302)        
        self.assertRedirects(res, reverse('users:register'))  
        
        self.login()
        res = self.client.get(reverse('users:userprofile'))
        self.assertEqual(res.status_code, 200)
        self.assertIsNotNone(res.context['form'])
        self.assertIsNotNone(res.context['userobj'])
        
    def test_profile_userid(self):
        res = self.client.get(reverse('users:userprofile' , kwargs={'user_id':901299012}))
        self.assertEqual(res.status_code, 404)       
    
        self.login()
        res = self.client.get(reverse('users:userprofile' , kwargs={'user_id':self.user.id}))
        self.assertEqual(res.status_code, 200)       
        self.assertIsNotNone(res.context['form'])
        self.assertIsNotNone(res.context['form2'])
        self.assertIsNotNone(res.context['form3'])
        self.assertIsNotNone(res.context['user_addresses'])
        self.assertIsNotNone(res.context['userobj'])
        
class UsersEditAddAdressViewTestCase(BaseUsersTestCase):        
    addresses = Address.objects.all()
        
    def test_editaddress_addressid(self):
        res = self.client.get(reverse('users:editaddress', kwargs={'address_id':self.addresses[1].id}))
        self.assertEqual(res.status_code, 302)    
        self.assertRedirects(res, reverse('users:login') + "?next=%s" % reverse('users:editaddress', kwargs={'address_id':self.addresses[1].id}))
        
        self.login()
        res = self.client.get(reverse('users:editaddress', kwargs={'address_id':self.addresses[1].id}))
        self.assertEqual(res.status_code, 200)  
        self.assertIsNotNone(res.context['form'])
        self.assertIsNotNone(res.context['user_address'])
        
    def test_addaddress(self):
        res = self.client.get(reverse('users:addaddress'))
        self.assertEqual(res.status_code, 302)        
        self.assertRedirects(res, reverse('users:login') + "?next=%s" % reverse('users:addaddress'))  
        
        self.login()
        res = self.client.get(reverse('users:addaddress'))
        self.assertEqual(res.status_code, 200)       
        self.assertIsNotNone(res.context['form'])
        
class UsersDeleteAdressViewTestCase(BaseUsersTestCase):        
    addresses = Address.objects.all()
    
    def test_deleteaddress(self):
        res = self.client.get(reverse('users:deleteaddress'))  
        self.assertEqual(res.status_code, 302)
        self.assertRedirects(res, reverse('users:login') + "?next=%s" % reverse('users:deleteaddress'))  
        
        self.login()
        res = self.client.get(reverse('users:deleteaddress'))
        self.assertEqual(res.status_code, 302)
        self.assertRedirects(res, reverse('users:userprofile'))  
        
    def test_deleteaddress_addressid(self):
        res = self.client.get(reverse('users:deleteaddress', kwargs={'address_id':self.addresses[1].id}))
        self.assertEqual(res.status_code, 302)
        self.assertRedirects(res, reverse('users:login') + "?next=%s" % reverse('users:deleteaddress', kwargs={'address_id':self.addresses[1].id}))  
        
        self.login()
        res = self.client.get(reverse('users:deleteaddress', kwargs={'address_id':self.addresses[1].id}))
        self.assertEqual(res.status_code, 302)
        self.assertRedirects(res, reverse('users:userprofile'))
