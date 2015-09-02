from django.test import TestCase
from django.contrib.auth.models import User
from .models import Member, Address
from django.core.urlresolvers import reverse


class BaseUsersTestCase(TestCase):

    fixtures = ['users_views_testdata.json', 'auth_views_testdata.json']

    all_users = User.objects.all()
    all_addresses = Address.objects.all()
    all_members = Member.objects.all()

    def login(self, uname='admin', password='admin'):
        res = self.client.post(reverse('users:login'),
                               {'username': uname, 'password': password})
        self.assertEqual(res.status_code, 302)
        # self.assertRedirects(res, reverse('users:index'))
        self.assertIn('_auth_user_id', self.client.session)
        self.user = User.objects.get(username=uname)

        self.user_addresses = Address.objects.filter(resident=self.user)
        self.user_member = Member.objects.get(user=self.user)

        self.not_users = User.objects.exclude(username=uname)
        self.not_user_addresses = Address.objects.exclude(resident=self.user)


class UsersIndexViewTestCase(BaseUsersTestCase):
    def test_index(self):
        res = self.client.get(reverse('users:index'))
        self.assertEqual(res.status_code, 302)

        self.login()
        res = self.client.get(reverse('users:index'))
        self.assertEqual(res.status_code, 200)


class UsersProfileViewTestCase(BaseUsersTestCase):
    def test_viewing_own_profile(self):
        # view own profile
        # not logged in
        res = self.client.get(reverse('users:profile'))
        self.assertEqual(res.status_code, 302)
        self.assertRedirects(res, reverse('users:register'))

        # logged in
        self.login()
        res = self.client.get(reverse('users:profile'))
        self.assertEqual(res.status_code, 200)
        self.assertIsNotNone(res.context['form'])
        self.assertIsNotNone(res.context['userobj'])

    def test_viewing_other_user_profiles(self):
        # not logged in
        res = self.client.get(reverse('users:profile',
                                      kwargs={'user_id':
                                              self.all_users[0].id}))
        self.assertEqual(res.status_code, 200)

        res = self.client.get(reverse('users:profile',
                                      kwargs={'user_id': 901299012}))
        self.assertEqual(res.status_code, 404)

        # logged in
        self.login()
        res = self.client.get(reverse('users:profile',
                                      kwargs={'user_id': self.user.id}))
        self.assertEqual(res.status_code, 200)
        self.assertIsNotNone(res.context['form'])
        self.assertIsNotNone(res.context['form2'])
        self.assertIsNotNone(res.context['form3'])
        self.assertIsNotNone(res.context['user_addresses'])
        self.assertIsNotNone(res.context['userobj'])

        res = self.client.get(reverse('users:profile',
                                      kwargs={'user_id': 901299012}))
        self.assertEqual(res.status_code, 404)


class UsersEditAddAdressViewTestCase(BaseUsersTestCase):
    def test_add_address(self):
        # Should I test '@login_required'?
        self.login()

        # add address
        res = self.client.get(reverse('users:add_address'))
        self.assertEqual(res.status_code, 200)
        self.assertIsNotNone(res.context['form'])

    def test_edit_address(self):
        # Should I test '@login_required'?
        self.login()

        # edit own address
        res = self.client.get(reverse('users:edit_address',
                                      kwargs={'address_id':
                                              self.user_addresses[0].id}))
        self.assertEqual(res.status_code, 200)
        self.assertIsNotNone(res.context['form'])
        self.assertIsNotNone(res.context['user_address'])

        # edit not own address
        res = self.client.get(reverse('users:edit_address',
                                      kwargs={'address_id':
                                              self.not_user_addresses[0].id}))
        self.assertEqual(res.status_code, 302)
        self.assertRedirects(res, reverse('users:profile'))

        # edit nonexistent address
        res = self.client.get(reverse('users:edit_address',
                                      kwargs={'address_id': 9876543210}))
        self.assertEqual(res.status_code, 404)


class UsersDeleteAdressViewTestCase(BaseUsersTestCase):
    def test_delete_address_addressid(self):
        # Should I test '@login_required'?
        self.login()

        # delete own address
        res = self.client.get(reverse('users:delete_address',
                                      kwargs={'address_id':
                                              self.user_addresses[0].id}))
        self.assertEqual(res.status_code, 302)
        self.assertRedirects(res, reverse('users:add_address'))

        # delete not own address
        res = self.client.get(reverse('users:delete_address',
                                      kwargs={'address_id':
                                              self.not_user_addresses[0].id}))
        self.assertEqual(res.status_code, 302)
        self.assertRedirects(res, reverse('users:add_address'))

        # delete nonexistent address
        res = self.client.get(reverse('users:delete_address',
                                      kwargs={'address_id': 9876543210}))
        self.assertEqual(res.status_code, 404)
