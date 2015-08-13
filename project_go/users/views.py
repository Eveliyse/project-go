from django.shortcuts import get_object_or_404, render, render_to_response, redirect
from django.template import RequestContext
from django.contrib.auth import login as django_login, authenticate, logout as django_logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm, SetPasswordForm
from django.contrib.auth.models import User
from .models import Member, Address, Country
from users.forms import MemberAddressForm, MemberDetailsForm, UserCreateForm, UserEditForm

#placeholder for now
def index(request):
    return render(request, 'users/index.html')

def profile(request, user_id=None):
    """ If the user is viewing own profile then let them edit things
        Otherwise, show basic details of user
    """    
    #convert supplied userid to int
    if user_id:
        u_id = int(user_id)
    elif request.user.is_authenticated():
        u_id = int(request.user.id)
    else:
        return redirect('/users/register')
    
    #Get user and member objects based on supplied userid
    user = get_object_or_404(User, id = u_id)
    member = get_object_or_404(Member, user = user)
    
    #if POST then process forms, else create a new user_edit_form
    #TODO check if password fields changed before validating
    if request.method == "POST":
        user_edit_form = UserEditForm(data=request.POST, instance = user, prefix="user")
        password_edit_form = SetPasswordForm(data=request.POST, user = user, prefix="password")
        member_edit_form = MemberDetailsForm(data=request.POST, instance = member, prefix="member")
        if user_edit_form.is_valid():
            user_edit_form.save()
        if password_edit_form.is_valid():
            password_edit_form.save()
        if member_edit_form.is_valid():
            member_edit_form.save()
        return render_to_response('users/profile.html', {
            'form': user_edit_form,
            'form2': password_edit_form,
            'form3': member_edit_form,
            'userobj' : user
            }, context_instance=RequestContext(request))
    else:
        user_edit_form = UserEditForm(instance = user, prefix="user")        
    
    #if user is viewing own profile then create forms for editing details and fetch data to display.
    #else the user is viewing not own profile so just process the 1 form
    if u_id == request.user.id:
        password_edit_form = SetPasswordForm(user = user, prefix="password")
        member_edit_form = MemberDetailsForm(instance = member, prefix="member")
        
        a = Address.objects.filter(resident = request.user)
        
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

def login(request):
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
                        django_login(request, user)
                        return redirect('/users')
        else:
            form = AuthenticationForm()
        return render_to_response('users/login.html', {
            'form': form,
            }, context_instance=RequestContext(request))
    else:
        #TODO redirect somewhere more sensible
        return HttpResponseRedirect('/users/')    

#@login_required
def logout(request):
    django_logout(request)
    return HttpResponseRedirect('/users/')

def register(request):
    """ If POST then process forms and create relevant database entries
        Otherwise check if the user is already logged in. If not then show registration forms
    """    
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
            a = user_address_form.save(commit = False)
            a.resident = d
            a.save()       
            #TODO redirect somewhere more sensible
            return redirect('/users')
    elif not request.user.is_authenticated():
        user_create_form = UserCreateForm(prefix="user")
        user_details_form = MemberDetailsForm(prefix="userdetails")
        user_address_form = MemberAddressForm(prefix="address")
        return render_to_response('users/register.html', {
            'form': user_create_form,
            'form2': user_details_form,
            'form3': user_address_form,
            }, context_instance=RequestContext(request))
