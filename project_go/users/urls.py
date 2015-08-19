from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^$', views.Index, name='index'),
    url(r'^profile/$', views.Profile, name='userprofile'),
    url(r'^profile/(?P<user_id>\d+)/$', views.Profile, name='userprofile'),
    url(r'^profile/add-address/$', views.EditAddAddress, name='addaddress'),
    url(r'^profile/edit-address/$', views.EditAddAddress, name='editaddress'),
    url(r'^profile/edit-address/(?P<address_id>\d+)/$', views.EditAddAddress, name='editaddress'),
    url(r'^profile/delete-address/(?P<address_id>\d+)/$', views.DeleteAddress, name='deleteaddress'),
    url(r'^login/$', views.Login, name = 'login'),
    url(r'^logout/$', views.Logout, name = 'logout'),
    url(r'^register/$', views.Register, name = 'register'),
]
