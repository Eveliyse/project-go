from django.shortcuts import get_object_or_404, get_list_or_404, render, render_to_response, redirect
from django.template import RequestContext
from django.http import HttpResponse
from django.contrib.auth import login as django_login, authenticate, logout as django_logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm, SetPasswordForm
from django.contrib.auth.models import User
from .models import Member, Address, Country
from users.forms import MemberAddressForm, MemberDetailsForm, UserCreateForm, UserEditForm
from django.core.urlresolvers import reverse

#placeholder for now
def Index(request):
    return render(request, 'users/index.html')

def Profile(request, user_id=None):
    """ If the user is viewing own profile then let them edit things
        Otherwise, show basic details of 'other' user
    """    
    #if available, use a supplied id or current user's id.
    #Otherwise redirect user to register page
    if user_id:
        u_id = int(user_id)
    elif request.user.is_authenticated():
        u_id = int(request.user.id)
    else:
        return redirect(reverse('users:register'))
    
    #Get user and member objects based on supplied userid
    user = get_object_or_404(User, id = u_id)
    member = get_object_or_404(Member, user = user)
    
    #if POST then process forms, else create a new user_edit_form
    #TODO check if password fields actually have a value
    if request.method == "POST":
        user_edit_form = UserEditForm(data=request.POST, instance = user, prefix="user")
        password_edit_form = SetPasswordForm(data=request.POST, user = user, prefix="password", initial={})
        member_edit_form = MemberDetailsForm(data=request.POST, instance = member, prefix="member")
        
        if user_edit_form.is_valid():
            user_edit_form.save()
        if password_edit_form.has_changed():
            if password_edit_form.is_valid():
                password_edit_form.save()
        if member_edit_form.is_valid():
            member_edit_form.save()
    
    #create form for display
    user_edit_form = UserEditForm(instance = user, prefix="user")        
    
    #if user is viewing own profile then create forms for editing details and fetch data to display.
    #else the user is viewing not own profile so just process the 1 form
    if u_id == request.user.id:
        password_edit_form = SetPasswordForm(user = user, prefix="password", initial={})
        member_edit_form = MemberDetailsForm(instance = member, prefix="member")
        
        a = get_list_or_404(Address, resident = request.user, active = True)
        
        return render_to_response('users/profile.html', {
            'form': user_edit_form,
            'form2': password_edit_form,
            'form3': member_edit_form,
            'user_addresses' : a,
            'userobj' : user
            }, context_instance=RequestContext(request))
    else:
        return render_to_response('users/profile.html', {
            'form': user_edit_form,
            'userobj' : user
            }, context_instance=RequestContext(request))

@login_required
def EditAddAddress(request, address_id=None):
    #user_address_form = MemberAddressForm()
    if address_id:
        address = get_object_or_404(Address, id = address_id, active = True)
        if address.resident == request.user:
            if request.method == "POST":
                user_address_form = MemberAddressForm(data=request.POST, instance=address)
                if user_address_form.is_valid():
                    user_address_form.save()
        user_address_form = MemberAddressForm(instance=address)
        a = get_list_or_404(Address, resident = request.user, active = True)
        return render_to_response('users/edit-address.html', {
            'form': user_address_form,
            'user_address' : address,
            'user_addresses' : a,
            }, context_instance=RequestContext(request))    
    else:
        if request.method == "POST":
            user_address_form = MemberAddressForm(data=request.POST)
            if user_address_form.is_valid():
                a = user_address_form.save(commit = False)
                a.resident = request.user
                a.active = True
                a.save()
                return redirect(reverse('users:editaddress', kwargs={'address_id':a.id}))            
            else:
                #TODO do what if form invalid?
                return  HttpResponse("Boooom")
    user_address_form = MemberAddressForm()
    a = get_list_or_404(Address, resident = request.user, active = True)
    if(request.GET.has_key('ajax')):
        return render_to_response('users/edit-address.html', {
            'form': user_address_form,
            'user_address' : address,
            'user_addresses' : a,
            }, context_instance=RequestContext(request))
    return render_to_response('users/edit-address.html', {
        'form': user_address_form,
        'user_addresses' : a,
        }, context_instance=RequestContext(request))    
#    return redirect(reverser('users:userprofile'))
    
@login_required
def DeleteAddress(request, address_id=None):
    if address_id:
        address = get_object_or_404(Address, id = address_id, active = True)

        #if request.method == "POST":
        if address.resident == request.user:
                address.active = False
                address.save()
    return redirect(reverse('users:userprofile'))

def Login(request):
    """ If the user is already logged in then redirect somewhere else
        Otherwise, render template and form or process POST data
    """
    if not request.user.is_authenticated():
        if request.method == 'POST':
            form = AuthenticationForm(data=request.POST)
            if form.is_valid():
                user = authenticate(username=request.POST['username'], password=request.POST['password'])
                if user is not None:
                    if user.is_active:
                        django_login(request, form.get_user())
                        return redirect(reverse('users:index')) 
        else:
            form = AuthenticationForm()
        return render_to_response('users/login.html', {
            'form': form,
            }, context_instance=RequestContext(request))
    else:
        #TODO redirect somewhere more sensible
        return redirect(reverse('users:index')) 

@login_required
def Logout(request):
    django_logout(request)
    return redirect(reverse('users:index'))

def Register(request):
    """ If POST then process forms and create relevant database entries
        Otherwise check if the user is already logged in. If not then show registration forms
    """    
    if request.method == 'POST':
        user_create_form = UserCreateForm(data=request.POST, prefix="user")
        user_details_form = MemberDetailsForm(data=request.POST, prefix="userdetails")
        user_address_form = MemberAddressForm(data=request.POST, prefix="address")
        if user_create_form.is_valid() and user_details_form.is_valid() and user_address_form.is_valid():
            user = user_create_form.save()            
            u = User.objects.get(username=user.username)
            u.is_staff = False
            u.save()                     
            d = user_details_form.save(commit = False)
            d.user = user
            d.save()
            a = user_address_form.save(commit = False)
            a.resident = user
            a.active = True
            a.save()       
            #TODO redirect somewhere more sensible
            return redirect(reverse('users:index'))
        else:
            return  HttpResponse("Boooom")        
    elif not request.user.is_authenticated():
        user_create_form = UserCreateForm(prefix="user")
        user_details_form = MemberDetailsForm(prefix="userdetails")
        user_address_form = MemberAddressForm(prefix="address")
        return render_to_response('users/register.html', {
            'form': user_create_form,
            'form2': user_details_form,
            'form3': user_address_form,
            }, context_instance=RequestContext(request))
    return redirect(reverse('users:index'))
