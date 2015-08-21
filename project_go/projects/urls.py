from django.conf.urls import url
from . import views
from projects.views import CreateProjectView, ManageProjectsView, DeletePledgeRewardsView, IndexView, UpdateStatusView

urlpatterns = [
    url(r'^$', IndexView.as_view(), name='index'),
    url(r'^manage/$', ManageProjectsView.as_view(), name='manage'),
    url(r'^create/$', CreateProjectView.as_view(), name='create'),
    url(r'^edit/(?P<project_id>\d+)/$', views.Edit, name='edit'),
    url(r'^update_status/(?P<project_id>\d+)/$', UpdateStatusView.as_view(), name='update_status'),
    url(r'^pledgerewards/(?P<project_id>\d+)/$', views.EditAddPledgeRewards, name='pledgerewards'),
    url(r'^pledgerewards/(?P<project_id>\d+)/p(?P<P_R_id>\d+)/$', views.EditAddPledgeRewards, kwargs=dict(mode="pledge"), name='pledge'),
    url(r'^pledgerewards/(?P<project_id>\d+)/r(?P<P_R_id>\d+)/$', views.EditAddPledgeRewards, kwargs=dict(mode="reward"), name='reward'),
    url(r'^pledgerewards/(?P<project_id>\d+)/p(?P<P_R_id>\d+)/delete/$', DeletePledgeRewardsView.as_view(), kwargs=dict(mode="pledge"), name='deletepledge'),
    url(r'^pledgerewards/(?P<project_id>\d+)/r(?P<P_R_id>\d+)/delete/$', DeletePledgeRewardsView.as_view(), kwargs=dict(mode="reward"), name='deletereward'),
    url(r'^details/$', views.Details, name='details'),
]
