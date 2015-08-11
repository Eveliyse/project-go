from django.shortcuts import render, render_to_response, redirect
from django.template import RequestContext
from django.http import HttpResponse
from django.shortcuts import HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login as django_login, authenticate, logout as django_logout
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib.auth.models import User
from .models import Member, Address, Country
from users.forms import MemberAddressForm, MemberDetailsForm, UserCreateForm
import datetime

#@login_required
def index(request):
    return render(request, 'users/index.html')

def login(request):
    if not request.user.is_authenticated():
        if request.method == 'POST':
            form = AuthenticationForm(data=request.POST)
            if form.is_valid():
                user = authenticate(username=request.POST['username'], password=request.POST['password'])
                if user is not None:
                    if user.is_active:
                        django_login(request, user)
                        return redirect('/users')
        else:
            form = AuthenticationForm()
        return render_to_response('users/login.html', {
            'form': form,
            }, context_instance=RequestContext(request))
    else:
        return HttpResponseRedirect('/users/')    

def logout(request):
    django_logout(request)
    return HttpResponseRedirect('/users/')

def register(request):
    if request.method == 'POST':
        user_create_form = UserCreateForm(data=request.POST, prefix="user")
        user_details_form = MemberDetailsForm(data=request.POST, prefix="userdetails")
        user_address_form = MemberAddressForm(data=request.POST, prefix="address")
        if user_create_form.is_valid() and user_details_form.is_valid() and user_address_form.is_valid():
            user_details_form = user_details_form.cleaned_data
            user_address_form = user_address_form.cleaned_data
            user = user_create_form.save()            
            u = User.objects.get(username=user.username)
            u.is_staff = False
            u.save()                     
            d = Member(user = u, dob = user_details_form['dob'])
            d.save()
            a = Address(resident = d,
                        line_1 = user_address_form['line_1'],
                        line_2 = user_address_form['line_2'],
                        town = user_address_form['town'],
                        postcode = user_address_form['postcode'],
                        country = user_address_form['country'],)
            a.save()       
            return redirect('/users')
    else:
        user_create_form = UserCreateForm(prefix="user")
        user_details_form = MemberDetailsForm(prefix="userdetails")
        user_address_form = MemberAddressForm(prefix="address")
    return render_to_response('users/register.html', {
        'form': user_create_form,
        'form2': user_details_form,
        'form3': user_address_form,
        }, context_instance=RequestContext(request))
