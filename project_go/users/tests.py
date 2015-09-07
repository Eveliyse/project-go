from django.test import TestCase
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse

from .models import Member, Address


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


class UsersLoginLogoutViewTestCase(BaseUsersTestCase):
    def test_logout(self):
        self.login()
        res = self.client.get(reverse('users:logout'))
        self.assertEqual(res.status_code, 302)


class UsersIndexViewTestCase(BaseUsersTestCase):
    def test_index(self):
        res = self.client.get(reverse('users:index'))
        self.assertEqual(res.status_code, 302)

        self.login()
        res = self.client.get(reverse('users:index'))
        self.assertEqual(res.status_code, 200)


class UsersCreateViewTestCase(BaseUsersTestCase):
    def test_view_create_user(self):
        res = self.client.get(reverse('users:register'))
        self.assertEqual(res.status_code, 200)

        self.login()
        res = self.client.get(reverse('users:register'))
        self.assertEqual(res.status_code, 302)

    def test_action_create_user(self):
        res = self.client.post(reverse('users:register'),
                               {'username': 'zac',
                                'first_name': 'zac',
                                'last_name': 'zac',
                                'email': 'zac@zac.com',
                                'password1': 'zac',
                                'password2': 'zac',
                                'dob_month': '1',
                                'dob_day': '1',
                                'dob_year': '2000',
                                'gender': '6',
                                'line_1': 'zac zouse',
                                'line_2': '',
                                'town': 'zac town',
                                'postcode': 'ZA12 1ZA',
                                'country': '30',
                                })
        self.assertEqual(res.status_code, 302)
        self.assertTrue(User.objects.filter(username='zac').exists())
        
        res = self.client.post(reverse('users:register'),
                               {'username': 'banana',
                                'first_name': 'banana',
                                'last_name': 'banana',
                                'email': 'banana@banana.com',
                                'password1': 'PWORD1',
                                'password2': 'PWORD2',
                                'dob_month': '1',
                                'dob_day': '1',
                                'dob_year': '2000',
                                'gender': '6',
                                'line_1': 'zac zouse',
                                'line_2': '',
                                'town': 'zac town',
                                'postcode': 'ZA12 1ZA',
                                'country': '30',
                                })
        self.assertEqual(res.status_code, 200)
        self.assertFalse(User.objects.filter(username='banana').exists())

        res = self.client.post(reverse('users:register'), {})
        self.assertEqual(res.status_code, 200)


class UsersProfileViewTestCase(BaseUsersTestCase):
    def test_view_noID_profile(self):
        # view own profile
        # not logged in
        res = self.client.get(reverse('users:profile'))
        self.assertEqual(res.status_code, 302)
        self.assertRedirects(res, reverse('users:register'))

        # logged in
        self.login()
        
        res = self.client.get(reverse('users:profile'))
        self.assertEqual(res.status_code, 200)

    def test_view_ID_profiles(self):
        # not logged in
        res = self.client.get(
            reverse('users:profile',
                    kwargs={'user_id': self.user.id}))
        self.assertEqual(res.status_code, 200)
        
        res = self.client.get(
            reverse('users:profile',
                    kwargs={'user_id': self.all_users[1].id}))
        self.assertEqual(res.status_code, 200)        

        res = self.client.get(
            reverse('users:profile', kwargs={'user_id': 987654321}))
        self.assertEqual(res.status_code, 404)

        # logged in
        self.login()
        res = self.client.get(
            reverse('users:profile', kwargs={'user_id': self.user.id}))
        self.assertEqual(res.status_code, 200)
        
        res = self.client.get(
            reverse('users:profile',
                    kwargs={'user_id': self.all_users[1].id}))
        self.assertEqual(res.status_code, 200)           

        res = self.client.get(
            reverse('users:profile', kwargs={'user_id': 987654321}))
        self.assertEqual(res.status_code, 404)

    def test_edit_profile(self):
        self.login()
        
        res = self.client.post(reverse('users:profile'), {})
        self.assertEqual(res.status_code, 200)
        
        self.assertFalse(User.objects.filter(first_name='zac').exists())
        res = self.client.post(
            reverse('users:profile'), {
                'first_name': 'zac',
                'last_name': 'zac',
                'email': 'zac@zac.com',
                'new_password1': '',
                'new_password2': '',
                'dob_month': '1',
                'dob_day': '1',
                'dob_year': '2000',
                'gender': '6',
            }
        )
        self.assertEqual(res.status_code, 200)
        self.assertTrue(User.objects.filter(first_name='zac').exists())

        res = self.client.post(
            reverse('users:profile'), {
                'first_name': 'zac',
                'last_name': 'zac',
                'email': 'zac@zac.com',
                'new_password1': 'zac',
                'new_password2': 'zac',
                'dob_month': '1',
                'dob_day': '1',
                'dob_year': '2000',
                'gender': '6',
            }
        )
        self.assertEqual(res.status_code, 302)


class UsersEditAddAdressViewTestCase(BaseUsersTestCase):
    def test_add_address(self):
        # Should I test '@login_required'?
        self.login()

        # view add address
        res = self.client.get(reverse('users:add_address'))
        self.assertEqual(res.status_code, 200)
        self.assertIsNotNone(res.context['form'])

        # add address
        res = self.client.post(reverse('users:add_address'),
                               {'line_1': 'zac\'s house',
                                'line_2': '',
                                'town': 'zac town',
                                'postcode': 'ZA12 3ZA',
                                'country': '35',
                                })
        self.assertEqual(res.status_code, 302)

    def test_edit_address(self):
        # Should I test '@login_required'?
        self.login()

        # view own address
        res = self.client.get(
            reverse('users:edit_address',
                    kwargs={'address_id': self.user_addresses[0].id}))
        self.assertEqual(res.status_code, 200)
        self.assertIsNotNone(res.context['form'])
        self.assertIsNotNone(res.context['user_address'])

        res = self.client.post(
            reverse('users:edit_address',
                    kwargs={'address_id': self.user_addresses[0].id}), {
                        'line_1': 'zac\'s house',
                        'line_2': '',
                        'town': 'zac town',
                        'postcode': 'ZA12 3ZA',
                        'country': '35',
                    })
        self.assertEqual(res.status_code, 200)

        # view not own address
        res = self.client.get(
            reverse('users:edit_address',
                    kwargs={'address_id': self.not_user_addresses[0].id}))
        self.assertEqual(res.status_code, 302)
        self.assertRedirects(res, reverse('users:profile'))

        # view nonexistent address
        res = self.client.get(
            reverse('users:edit_address', kwargs={'address_id': 9876543210}))
        self.assertEqual(res.status_code, 404)


class UsersDeleteAdressViewTestCase(BaseUsersTestCase):
    def test_delete_address_addressid(self):
        # Should I test '@login_required'?
        self.login()

        # delete own address
        res = self.client.get(
            reverse('users:delete_address',
                    kwargs={'address_id': self.user_addresses[0].id}))
        self.assertEqual(res.status_code, 302)
        self.assertRedirects(res, reverse('users:add_address'))

        # delete not own address
        res = self.client.get(
            reverse('users:delete_address',
                    kwargs={'address_id': self.not_user_addresses[0].id}))
        self.assertEqual(res.status_code, 302)
        self.assertRedirects(res, reverse('users:add_address'))

        # delete nonexistent address
        res = self.client.get(
            reverse('users:delete_address', kwargs={'address_id': 9876543210}))
        self.assertEqual(res.status_code, 404)
