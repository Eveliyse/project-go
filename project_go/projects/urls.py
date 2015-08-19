from django.conf.urls import url
from . import views
from projects.views import CreateProjectView

urlpatterns = [
    url(r'^$', views.Index, name='index'),
    url(r'^manage/$', views.Index, name='manage'),
    url(r'^create/$', CreateProjectView.as_view(), name='create'),
    url(r'^edit/(?P<project_id>\d+)/$', views.Edit, name='edit'),
    url(r'^pledgerewards/(?P<project_id>\d+)/$', views.EditAddPledgeRewards, name='pledgerewards'),
    url(r'^pledgerewards/(?P<project_id>\d+)/p(?P<P_R_id>\d+)/$', views.EditAddPledgeRewards, kwargs=dict(mode="pledge"), name='pledge'),
    url(r'^pledgerewards/(?P<project_id>\d+)/r(?P<P_R_id>\d+)/$', views.EditAddPledgeRewards, kwargs=dict(mode="reward"), name='reward'),
    url(r'^pledgerewards/(?P<project_id>\d+)/p(?P<P_R_id>\d+)/delete/$', views.DeletePledgeRewards, kwargs=dict(mode="pledge"), name='deletepledge'),
    url(r'^pledgerewards/(?P<project_id>\d+)/r(?P<P_R_id>\d+)/delete/$', views.DeletePledgeRewards, kwargs=dict(mode="reward"), name='deletereward'),
    url(r'^details/$', views.Details, name='details'),
]
