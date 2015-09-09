from django.conf.urls import url
from . import views
from django.contrib.auth import views as auth_views
from users.views import (
    ViewUserProfile,
    EditUserProfile,
    CreateAddressView,
    EditAddressView,
    DeleteAddressView)

urlpatterns = [
    url(r'^$', views.Profile, name='index'),
    url(r'^profile/$', EditUserProfile.as_view(), name='profile'),
    url(r'^profile/(?P<user_id>\d+)/$', ViewUserProfile.as_view(), name='profile'),
    url(r'^profile/add-address/$', CreateAddressView.as_view(), name='add_address'),
    url(r'^profile/edit-address/$', CreateAddressView.as_view(), name='edit_address'),
    url(r'^profile/edit-address/(?P<address_id>\d+)/$', EditAddressView.as_view(), name='edit_address'),
    url(r'^profile/delete-address/(?P<address_id>\d+)/$', DeleteAddressView.as_view(), name='delete_address'),
    url(r'^login/$', auth_views.login, {'template_name': 'users/login.html'}, name='login'),
    url(r'^logout/$', views.Logout, name='logout'),
    url(r'^register/$', views.Register, name='register'),
]
