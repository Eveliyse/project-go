from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^manage/$', views.index, name='manage'),
    url(r'^create/$', views.create, name='create'),
    url(r'^edit/(?P<project_id>\d+)/$', views.edit, name='edit'),
    url(r'^pledgerewards/(?P<project_id>\d+)/$', views.pledgerewards, name='pledgerewards'),
    url(r'^details/$', views.details, name='details'),
]
