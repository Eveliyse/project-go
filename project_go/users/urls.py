from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^profile/$', views.profile, name='userprofile'),
    url(r'^profile/(?P<user_id>\d+)/$', views.profile, name='othersprofile'),
    url(r'^profile/add-address/$', views.editaddaddress, name='addaddress'),
    url(r'^profile/edit-address/(?P<address_id>\d+)/$', views.editaddaddress, name='editaddress'),
    url(r'^profile/delete-address/(?P<address_id>\d+)/$', views.deleteaddress, name='deleteaddress'),
    url(r'^login/$', views.login, name = 'login'),
    url(r'^logout/$', views.logout, name = 'logout'),
    url(r'^register/$', views.register, name = 'register'),
]
