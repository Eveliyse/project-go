from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^manage/$', views.index, name='manage'),
    url(r'^create/$', views.create, name='create'),
    url(r'^edit/(?P<id>\d+)/$', views.edit, name='edit'),
    url(r'^details/$', views.details, name='details'),
]
