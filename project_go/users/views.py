from django.shortcuts import (get_object_or_404,
                              get_list_or_404,
                              render_to_response,
                              redirect)
from django.core.urlresolvers import reverse
from django.template import RequestContext
from django.contrib.auth import (login as auth_login,
                                 logout as auth_logout,
                                 authenticate)
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import (AuthenticationForm,
                                       SetPasswordForm)
from django.contrib.auth.models import User
from .models import Member, Address
from projects.models import Project, UserPledge
from users.forms import (MemberAddressForm, MemberDetailsForm,
                         UserCreateForm, UserEditForm)


# placeholder for now
def Index(request):
    return render_to_response("users/index.html",
                              context_instance=RequestContext(request))


def Profile(request, user_id=None):
    """ If the user is viewing own profile then let them edit things
        Otherwise, show basic details of 'other' user
    """
    # if available, use a supplied id or grab current user's id.
    # Otherwise redirect user to register page
    if user_id:
        u_id = int(user_id)
    elif request.user.is_authenticated():
        u_id = int(request.user.id)
    else:
        return redirect(reverse('users:register'))

    # Get user and member objects based on supplied userid
    user = get_object_or_404(User, id=u_id)
    member = get_object_or_404(Member, user=user)

    # if POST then process forms
    # TODO check if password fields actually have a value
    if request.method == "POST":
        user_edit_form = UserEditForm(data=request.POST, instance=user)
        password_edit_form = SetPasswordForm(data=request.POST,
                                             user=user,
                                             initial={})
        member_edit_form = MemberDetailsForm(data=request.POST,
                                             instance=member)

        if user_edit_form.is_valid():
            user_edit_form.save()
        if password_edit_form.has_changed():
            if password_edit_form.is_valid():
                password_edit_form.save()
        if member_edit_form.is_valid():
            member_edit_form.save()

    # create form for display
    user_edit_form = UserEditForm(instance=user)

    # get user pledged projects for display
    userpledges = UserPledge.objects.filter(user_id=u_id)
    pledge_projects = Project.objects.filter(
        project_pledges__pledged_users__user_id=u_id)

    # if user is viewing own profile then create forms for editing details
    # and fetch data to display. Else the user is viewing not own profile
    # so just process the 1 form
    if u_id == request.user.id:
        password_edit_form = SetPasswordForm(user=user, initial={})
        member_edit_form = MemberDetailsForm(instance=member)

        a = get_list_or_404(Address, resident=request.user, active=True)

        return render_to_response('users/profile.html', {
            'form': user_edit_form,
            'form2': password_edit_form,
            'form3': member_edit_form,
            'user_addresses': a,
            'userobj': user,
            'projects': pledge_projects,
            'userpledges': userpledges,
            }, context_instance=RequestContext(request))
    else:
        return render_to_response('users/profile.html', {
            'form': user_edit_form,
            'userobj': user,
            'projects': pledge_projects,
            }, context_instance=RequestContext(request))


@login_required
# TODO make ajax call only div
def EditAddAddress(request, address_id=None):
    # initialise user address form. Do this at the start
    # so render has something to fall back on
    user_address_form = MemberAddressForm()

    # if there is an address id then user is editing, not adding
    if address_id:
        # check address exists and belongs to current logged in user
        address = get_object_or_404(Address, id=address_id, active=True)
        if address.resident != request.user:
            return redirect(reverse('users:profile'))

        # if post then user is trying to edit an existing address
        if request.method == "POST":
            user_address_form = MemberAddressForm(data=request.POST,
                                                  instance=address)
            if user_address_form.is_valid():
                user_address_form.save()
        else:
            user_address_form = MemberAddressForm(instance=address)
    else:
        # if post then user is trying to add a new address
        if request.method == "POST":
            user_address_form = MemberAddressForm(data=request.POST)
            if user_address_form.is_valid():
                saved_address = user_address_form.save(commit=False)
                saved_address.resident = request.user
                saved_address.active = True
                saved_address.save()
                return redirect(reverse('users:edit_address',
                                kwargs={'address_id': saved_address.id}))

    # get list of user addresses. Do this at the end and not at start
    # incase we have added or edited addresses
    a = get_list_or_404(Address, resident=request.user, active=True)
    if address_id:
        return render_to_response('users/edit-address.html', {
            'form': user_address_form,
            'user_address': address,
            'user_addresses': a,
            }, context_instance=RequestContext(request))
    return render_to_response('users/edit-address.html', {
        'form': user_address_form,
        'user_addresses': a,
        }, context_instance=RequestContext(request))


@login_required
def DeleteAddress(request, address_id=None):
    if address_id:
        address = get_object_or_404(Address, id=address_id, active=True)

        if address.resident == request.user:
                address.active = False
                address.save()
    return redirect(reverse('users:add_address'))


def Login(request):
    """ If the user is already logged in then redirect somewhere else
        Otherwise, render template and form or process POST data
    """
    if not request.user.is_authenticated():
        if request.method == 'POST':
            form = AuthenticationForm(data=request.POST)
            if form.is_valid():
                user = authenticate(username=request.POST['username'],
                                    password=request.POST['password'])
                if user is not None:
                    if user.is_active:
                        auth_login(request, form.get_user())
                        return redirect(reverse('projects:index'))
        else:
            form = AuthenticationForm()
        return render_to_response('users/login.html', {
            'form': form,
            }, context_instance=RequestContext(request))
    else:
        # TODO redirect somewhere more sensible
        return redirect(reverse('projects:index'))


@login_required
def Logout(request):
    auth_logout(request)
    return redirect(reverse('projects:index'))


def Register(request):
    """ If POST then process forms and create relevant database entries
        Otherwise check if the user is already logged in.
        If not then show registration forms.
    """
    if request.method == 'POST':
        user_create_form = UserCreateForm(data=request.POST)
        user_details_form = MemberDetailsForm(data=request.POST)
        user_address_form = MemberAddressForm(data=request.POST)
        if (user_create_form.is_valid() and
                user_details_form.is_valid() and
                user_address_form.is_valid()):
            user = user_create_form.save()
            user.is_staff = False
            user.save()

            details = user_details_form.save(commit=False)
            details.user = user
            details.save()

            address = user_address_form.save(commit=False)
            address.resident = user
            address.active = True
            address.save()
            # TODO redirect somewhere more sensible? login?
            return redirect(reverse('users:login'))
        else:
            return render_to_response('users/register.html', {
                'form': user_create_form,
                'form2': user_details_form,
                'form3': user_address_form,
                }, context_instance=RequestContext(request))
    elif not request.user.is_authenticated():
        user_create_form = UserCreateForm()
        user_details_form = MemberDetailsForm()
        user_address_form = MemberAddressForm()
        return render_to_response('users/register.html', {
            'form': user_create_form,
            'form2': user_details_form,
            'form3': user_address_form,
            }, context_instance=RequestContext(request))
    return redirect(reverse('users:index'))
