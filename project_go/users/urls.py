from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^$', views.index, name='index'),
    #url(r'^signin/$', views.signin, name='signin'),
    #url(r'^login/$', 'django.contrib.auth.views.login', {'template_name': 'users/signin.html'}, name = 'login'),
    url(r'^login/$', views.login, name = 'login'),
    url(r'^logout/$', views.logout, name = 'logout'),
    url(r'^register/$', views.register, name = 'register'),
]
