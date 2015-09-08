from django.test import TestCase
from django.contrib.auth.models import User
from .models import Project, Reward, Pledge, Category, Status
from django.core.urlresolvers import reverse


class BaseProjectsTestCase(TestCase):
    # load test data
    fixtures = ['projects_views_testdata.json', 'auth_views_testdata.json']

    all_projects = Project.objects.all()
    all_pledges = Pledge.objects.all()
    all_rewards = Reward.objects.all()    

    new_status = Status.objects.get(status="New")
    open_status = Status.objects.get(status="Open")
    closed_status = Status.objects.get(status="Closed")
    
    new_projs = Project.objects.filter(status=new_status)
    open_projs = Project.objects.filter(status=open_status)
    closed_projs = Project.objects.filter(status=closed_status)    

    def login(self, uname='elsa', password='elsa'):
        res = self.client.post(
            reverse('users:login'),
            {'username': uname, 'password': password})
        self.assertEqual(res.status_code, 302)
        # self.assertRedirects(res, reverse('users:index'))
        self.assertIn('_auth_user_id', self.client.session)
        self.user = User.objects.get(username=uname)

        # create sets related to user
        self.user_projs = Project.objects.filter(owner=self.user)
        self.user_pledges = Pledge.objects.filter(
            project__id__in=self.user_projs)
        self.user_rewards = Reward.objects.filter(
            project__id__in=self.user_projs)

        self.new_projs = self.user_projs.filter(status=self.new_status)
        self.open_projs = self.user_projs.filter(status=self.open_status)
        self.closed_projs = self.user_projs.filter(status=self.closed_status)

        # create sets not related to user
        self.not_user_projs = Project.objects.exclude(owner=self.user)
        self.not_user_pledges = Pledge.objects.exclude(
            project__id__in=self.user_projs)
        self.not_user_rewards = Reward.objects.exclude(
            project__id__in=self.user_projs)


class ProjectsIndexTests(BaseProjectsTestCase):
    def test_index(self):
        # not logged in
        res = self.client.get(reverse('projects:index'))
        self.assertEqual(res.status_code, 200)

        # logged in
        self.login()
        res = self.client.get(reverse('projects:index'))
        self.assertEqual(res.status_code, 200)


class ProjectsManageTests(BaseProjectsTestCase):
    def test_view_manage_projects(self):
        # not logged in
        res = self.client.get(reverse('projects:manage'))
        self.assertEqual(res.status_code, 302)
        self.assertRedirects(res, reverse('users:login') +
                             "?next=%s" % reverse('projects:manage'))

        # logged in
        self.login()
        res = self.client.get(reverse('projects:manage'))
        self.assertEqual(res.status_code, 200)


class ProjectsCreateTests(BaseProjectsTestCase):
    def test_view_create_project(self):
        # not logged in
        res = self.client.get(reverse('projects:create'))
        self.assertEqual(res.status_code, 302)
        self.assertRedirects(res, reverse('users:login') +
                             "?next=%s" % reverse('projects:create'))

        # logged in
        self.login()
        res = self.client.get(reverse('projects:create'))
        self.assertEqual(res.status_code, 200)
        self.assertIsNotNone(res.context['form'])

    def test_action_create_project(self):
        self.login()
        with open('projects/test_img.jpg') as img:
            res = self.client.post(reverse('projects:create'),
                                   {'title': 'PROJECT X',
                                    'goal': '666',
                                    'image': img,
                                    'short_desc': 'short desc',
                                    'long_desc': 'long desc',
                                    'category': '6',
                                    })
        self.assertEqual(res.status_code, 302)

        with open('projects/test_img.jpg') as img:
            res = self.client.post(reverse('projects:create'),
                                   {'title': 'PROJECT X',
                                    'goal': 'abc',
                                    'image': img,
                                    'short_desc': 'short desc',
                                    'long_desc': 'long desc',
                                    'category': '6',
                                    })
        self.assertEqual(res.status_code, 200)


class ProjectsEditTests(BaseProjectsTestCase):
    def test_view_edit_project(self):
        # Should I test '@login_required'?
        self.login()

        # edit own project
        res = self.client.get(
            reverse('projects:edit',
                    kwargs={'project_id': self.new_projs[0].id}))
        self.assertEqual(res.status_code, 200)
        self.assertIsNotNone(res.context['form'])
        self.assertIsNotNone(res.context['pledgerewards'])
        self.assertIsNotNone(res.context['project'])

        res = self.client.get(
            reverse('projects:edit',
                    kwargs={'project_id': self.open_projs[0].id}))
        self.assertEqual(res.status_code, 302)

        res = self.client.get(
            reverse('projects:edit',
                    kwargs={'project_id': self.closed_projs[0].id}))
        self.assertEqual(res.status_code, 302)

        # edit not own project
        res = self.client.get(
            reverse('projects:edit',
                    kwargs={'project_id': self.not_user_projs[0].id}))
        self.assertEqual(res.status_code, 302)
        self.assertRedirects(res, reverse('projects:manage'))

        # edit nonexistent project
        res = self.client.get(
            reverse('projects:edit',
                    kwargs={'project_id': 9876543210}))
        self.assertEqual(res.status_code, 404)

        # edit no project
        res = self.client.get(reverse('projects:edit'))
        self.assertEqual(res.status_code, 302)

    def test_action_edit_project(self):
        self.login()
        
        with open('projects/test_img.jpg') as img:
            res = self.client.post(
                reverse('projects:edit',
                        kwargs={'project_id': self.new_projs[0].id}),
                {'title': 'PROJECT X',
                 'goal': '666',
                 'image': img,
                 'short_desc': 'short desc',
                 'long_desc': 'long desc',
                 'category': '6',
                 })
        self.assertEqual(res.status_code, 200)
        
        with open('projects/test_img.jpg') as img:
            res = self.client.post(
                reverse('projects:edit',
                        kwargs={'project_id': self.new_projs[0].id}),{})
        self.assertEqual(res.status_code, 200)
        
        with open('projects/test_img.jpg') as img:
            res = self.client.post(
                reverse('projects:edit',
                        kwargs={'project_id': self.new_projs[0].id}),
                {'title': '',
                 'goal': '',
                 'image': '',
                 'short_desc': '',
                 'long_desc': '',
                 'category': '',
                 })
        self.assertEqual(res.status_code, 200)
        # no error messages?


class ProjectsPledgeRewardsTests(BaseProjectsTestCase):
    def test_view_add_pledgerewards(self):
        # Should I test '@login_required'?
        self.login()

        # add pledge/rewards to own project
        res = self.client.get(
            reverse('projects:pledgerewards',
                    kwargs={'project_id': self.new_projs[0].id}))
        self.assertEqual(res.status_code, 200)
        self.assertIsNotNone(res.context['form2'])
        self.assertIsNotNone(res.context['form3'])
        self.assertIsNotNone(res.context['pledges'])
        self.assertIsNotNone(res.context['rewards'])
        self.assertIsNotNone(res.context['project'])

        res = self.client.get(
            reverse('projects:pledgerewards',
                    kwargs={'project_id': self.open_projs[0].id}))
        self.assertEqual(res.status_code, 302)

        res = self.client.get(
            reverse('projects:pledgerewards',
                    kwargs={'project_id': self.closed_projs[0].id}))
        self.assertEqual(res.status_code, 302)

        # add pledge/rewards to not own project
        res = self.client.get(
            reverse('projects:pledgerewards',
                    kwargs={'project_id': self.not_user_projs[0].id}))
        self.assertEqual(res.status_code, 302)
        self.assertRedirects(res, reverse('projects:manage'))

        # add pledge/rewards to nonexistent project
        res = self.client.get(
            reverse('projects:pledgerewards',
                    kwargs={'project_id': 9876543210}))
        self.assertEqual(res.status_code, 404)

    def test_action_add_pledgerewards(self):
        self.login()
        res = self.client.post(
            reverse('projects:pledgerewards',
                    kwargs={'project_id': self.new_projs[0].id}), {
                        'amount': '123',
                        'rewards': self.new_projs[0].project_pledges.all()[0].rewards.all()[0].id,
                    }
        )
        self.assertEqual(res.status_code, 200)

    def test_view_edit_pledgereward(self):
        # Should I test '@login_required'?
        self.login()

        # edit pledge for own project
        res = self.client.get(
            reverse('projects:pledge',
                    kwargs={'project_id': self.new_projs[0].id,
                            'P_R_id': (self.new_projs[0].project_pledges
                                       .all()[0].id)}))
        self.assertEqual(res.status_code, 200)
        self.assertIsNotNone(res.context['form2'])
        self.assertIsNotNone(res.context['form3'])
        self.assertIsNotNone(res.context['mode'])
        self.assertIsNotNone(res.context['instance'])
        self.assertIsNotNone(res.context['pledges'])
        self.assertIsNotNone(res.context['rewards'])
        self.assertIsNotNone(res.context['project'])

        res = self.client.get(
            reverse('projects:pledge',
                    kwargs={'project_id': self.open_projs[0].id,
                            'P_R_id': (self.open_projs[0].project_pledges
                                       .all()[0].id)}))
        self.assertEqual(res.status_code, 302)

        res = self.client.get(
            reverse('projects:pledge',
                    kwargs={'project_id':
                            self.closed_projs[0].id,
                            'P_R_id': (self.closed_projs[0].project_pledges
                                       .all()[0].id)}))
        self.assertEqual(res.status_code, 302)

        # edit pledge for not own project
        res = self.client.get(
            reverse('projects:pledge',
                    kwargs={
                        'project_id': (self.not_user_pledges[0].project.id),
                        'P_R_id': self.not_user_pledges[0].id}))
        self.assertEqual(res.status_code, 302)
        self.assertRedirects(res, reverse('projects:manage'))

        # edit nonexistnet pledge
        res = self.client.get(
            reverse('projects:pledge',
                    kwargs={'project_id': self.new_projs[0].id,
                            'P_R_id': 9876543210}))
        self.assertEqual(res.status_code, 404)

    def test_action_edit_pledgerewards(self):
        self.login()
        res = self.client.post(
            reverse('projects:pledge',
                    kwargs={'project_id': self.new_projs[0].id,
                            'P_R_id': (self.new_projs[0].project_pledges.all()[0].id)}), {
                                'amount': '123',
                                'rewards': self.new_projs[0].project_pledges
                                .all()[0].rewards.all()[0].id,
                            }
        )
        self.assertEqual(res.status_code, 200)

        res = self.client.post(
            reverse('projects:pledge',
                    kwargs={'project_id': self.not_user_projs[0].id,
                            'P_R_id': (self.not_user_projs[0].project_pledges.all()[0].id)}), {
                                'amount': '123',
                                'rewards': self.not_user_projs[0].project_pledges
                                .all()[0].rewards.all()[0].id,
                            }
        )
        self.assertEqual(res.status_code, 302)

    def test_view_reward(self):
        # Should I test '@login_required'?
        self.login()

        # edit reward for own project
        res = self.client.get(
            reverse('projects:reward',
                    kwargs={'project_id': self.new_projs[0].id,
                            'P_R_id': (self.new_projs[0].project_pledges
                                       .all()[0].rewards.all()[0].id)}))
        self.assertEqual(res.status_code, 200)
        self.assertIsNotNone(res.context['form2'])
        self.assertIsNotNone(res.context['form3'])
        self.assertIsNotNone(res.context['mode'])
        self.assertIsNotNone(res.context['instance'])
        self.assertIsNotNone(res.context['pledges'])
        self.assertIsNotNone(res.context['rewards'])
        self.assertIsNotNone(res.context['project'])

        res = self.client.get(
            reverse('projects:reward',
                    kwargs={'project_id': self.open_projs[0].id,
                            'P_R_id': (self.open_projs[0].project_pledges
                                       .all()[0].rewards.all()[0].id)}))
        self.assertEqual(res.status_code, 302)

        res = self.client.get(
            reverse('projects:reward',
                    kwargs={'project_id': self.closed_projs[0].id,
                            'P_R_id': (self.closed_projs[0].project_pledges
                                       .all()[0].rewards.all()[0].id)}))
        self.assertEqual(res.status_code, 302)

        # edit reward for not own project
        res = self.client.get(
            reverse('projects:reward',
                    kwargs={'project_id': self.not_user_rewards[0].project.id,
                            'P_R_id': self.not_user_rewards[0].id}))
        self.assertEqual(res.status_code, 302)
        self.assertRedirects(res, reverse('projects:manage'))

        # edit nonexistent reward
        res = self.client.get(
            reverse('projects:reward',
                    kwargs={'project_id': self.new_projs[0].id,
                            'P_R_id': 9876543210}))
        self.assertEqual(res.status_code, 404)

    def test_action_add_reward(self):
        self.login()
        res = self.client.post(
            reverse('projects:pledgerewards', kwargs={'project_id': self.new_projs[0].id}),
            {'desc': '123'})
        self.assertEqual(res.status_code, 200)

    def test_action_edit_reward(self):
        self.login()
        res = self.client.post(
            reverse('projects:reward',
                    kwargs={'project_id': self.new_projs[0].id,
                            'P_R_id': (self.new_projs[0].project_pledges
                                       .all()[0].rewards.all()[0].id)}), {
                                           'desc': '123',
                                       }
        )
        self.assertEqual(res.status_code, 200)

        res = self.client.post(
            reverse('projects:reward',
                    kwargs={'project_id': self.not_user_projs[0].id,
                            'P_R_id': (self.not_user_projs[0].project_pledges
                                       .all()[0].rewards.all()[0].id)}), {
                                           'desc': '123',
                                       }
        )
        self.assertEqual(res.status_code, 302)


class ProjectsPledgeRewardsDeleteTests(BaseProjectsTestCase):
    def test_delete_pledgereward(self):
        # Should I test '@login_required'?
        self.login()

        # delete pledge for own project
        res = self.client.get(
            reverse('projects:delete_pledge',
                    kwargs={'project_id': self.new_projs[0].id,
                            'P_R_id': (self.new_projs[0].project_pledges
                                       .all()[0].id)}))
        self.assertEqual(res.status_code, 302)
        self.assertRedirects(res,
                             reverse('projects:pledgerewards',
                                     kwargs={
                                         'project_id': self.new_projs[0].id}))

        # delete pledge for not own project
        res = self.client.get(
            reverse('projects:delete_pledge',
                    kwargs={'project_id': self.not_user_pledges[0].project.id,
                            'P_R_id': self.not_user_pledges[0].id}))
        self.assertEqual(res.status_code, 302)
        self.assertRedirects(res, reverse('projects:manage'))

        # delete nonexistent pledge
        res = self.client.get(
            reverse('projects:delete_pledge',
                    kwargs={'project_id': self.user_pledges[0].project.id,
                            'P_R_id': 9876543210}))
        self.assertEqual(res.status_code, 404)

    def test_delete_reward(self):
        # Should I test '@login_required'?
        self.login()

        # delete reward for own project
        res = self.client.get(
            reverse('projects:delete_reward',
                    kwargs={'project_id': self.new_projs[0].id,
                            'P_R_id': (self.new_projs[0].project_pledges
                                       .all()[0].rewards.all()[0].id)}))
        self.assertEqual(res.status_code, 302)
        self.assertRedirects(res,
                             reverse('projects:pledgerewards',
                                     kwargs={
                                         'project_id': self.new_projs[0].id}))

        # delete reward for not own project
        res = self.client.get(
            reverse(
                'projects:delete_reward',
                kwargs={
                    'project_id': self.not_user_rewards[0].project.id,
                    'P_R_id': self.not_user_rewards[0].id}))
        self.assertEqual(res.status_code, 302)
        self.assertRedirects(res, reverse('projects:manage'))

        # delete nonexistent reward
        res = self.client.get(
            reverse('projects:delete_reward',
                    kwargs={'project_id': self.user_rewards[0].project.id,
                            'P_R_id': 9876543210}))
        self.assertEqual(res.status_code, 404)


class ProjectsDetailsTests(BaseProjectsTestCase):
    def test_view_project_details(self):
        
        # not logged in
        res = self.client.get(reverse('projects:details',
                                      kwargs={'project_id': self.all_projects[0].id}))
        self.assertEqual(res.status_code, 200)

        res = self.client.get(reverse('projects:details',
                                      kwargs={'project_id': self.new_projs[0].id}))
        self.assertEqual(res.status_code, 302)

        res = self.client.get(reverse('projects:details',
                                      kwargs={'project_id': 9876543210}))
        self.assertEqual(res.status_code, 404)

        # logged in
        self.login()
        other_new_projs = Project.objects.filter(status=self.new_status).exclude(owner=self.user)

        # details for own project
        res = self.client.get(reverse('projects:details',
                                      kwargs={'project_id': self.user_projs[0].id}))
        self.assertEqual(res.status_code, 200)
        
        # details for not own new projects
        res = self.client.get(reverse('projects:details',
                                      kwargs={'project_id': other_new_projs[0].id}))
        self.assertEqual(res.status_code, 302)        

        # details for not own project
        self.login()
        res = self.client.get(reverse('projects:details',
                                      kwargs={'project_id': self.not_user_projs[0].id}))
        self.assertEqual(res.status_code, 200)

        # details for nonexistent project
        res = self.client.get(reverse('projects:details',
                                      kwargs={'project_id': 9876543210}))
        self.assertEqual(res.status_code, 404)


class ProjectsUpdateStatusTests(BaseProjectsTestCase):
    # TODO check status actually changed
    def test_update_project(self):
        self.login()

        res = self.client.post(reverse('projects:update_status',
                kwargs={'project_id': self.new_projs[0].id}))
        self.assertEqual(res.status_code, 302)

        res = self.client.post(reverse('projects:update_status',
                                       kwargs={'project_id': self.open_projs[0].id}))
        self.assertEqual(res.status_code, 302)

        res = self.client.post(reverse('projects:update_status',
                                       kwargs={'project_id': self.closed_projs[0].id}))
        self.assertEqual(res.status_code, 302)


class ProejctsAddUserPledgeTests(BaseProjectsTestCase):
    #TODO check pledge added
    def test_add_userpledge(self):
        self.login(uname='harry', password='harry')
        other_open_projs = Project.objects.filter(status=self.open_status).exclude(owner=self.user)

        res = self.client.get(reverse(
            'projects:add_pledge', kwargs={
                'project_id': other_open_projs[0].id,
                'pledge_id': other_open_projs[0].project_pledges.all()[0].id
            }))
        self.assertEqual(res.status_code, 302)        

    def test_change_userpledge(self):
        self.login()
        other_open_projs = Project.objects.filter(status=self.open_status).exclude(owner=self.user)

        res = self.client.get(reverse(
            'projects:add_pledge', kwargs={
                'project_id': other_open_projs[0].id,
                'pledge_id': other_open_projs[0].project_pledges.all()[0].id
            }))
        self.assertEqual(res.status_code, 302)

        res = self.client.get(reverse(
            'projects:add_pledge', kwargs={
                'project_id': other_open_projs[0].id,
                'pledge_id': other_open_projs[0].project_pledges.all()[1].id
            }))
        self.assertEqual(res.status_code, 302)


class ProjectsListTests(BaseProjectsTestCase):
    all_categories = Category.objects.all()

    def test_project_categories(self):
        # categories
        res = self.client.get(reverse('projects:category',
                                      kwargs={'category_id':
                                              self.all_categories[0].id}))
        self.assertEqual(res.status_code, 200)

        res = self.client.get(reverse('projects:category',
                                      kwargs={'category_id': 9876543210}))
        self.assertEqual(res.status_code, 404)

    def test_project_search(self):
        # search
        res = self.client.get(reverse('projects:search'))
        self.assertEqual(res.status_code, 200)

        res = self.client.get("%s?search_term=%s" %
                              (reverse('projects:search'),
                               self.all_projects[0].title))
        self.assertEqual(res.status_code, 200)

        res = self.client.get("%s?search_term=kjghskerhbgseserknguybserkgu" %
                              reverse('projects:search'))
        self.assertEqual(res.status_code, 200)

        res = self.client.get("%s?search_term= " %
                              reverse('projects:search'))
        self.assertEqual(res.status_code, 200)