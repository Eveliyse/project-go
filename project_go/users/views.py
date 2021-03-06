from django.conf import settings
from django.shortcuts import (
    get_object_or_404,
    get_list_or_404,
    render_to_response,
    redirect
)
from django.core.urlresolvers import reverse
from django.template import RequestContext
from django.http import HttpResponse
from django.views.generic import (
    CreateView,
    TemplateView,
    RedirectView,
    DetailView,
    ListView,
    UpdateView
)
from django.contrib.auth import (
    login as auth_login,
    logout as auth_logout,
    authenticate
)
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import redirect_to_login
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.models import User
from .models import Member, Address
from projects.models import Project, UserPledge
from users.forms import (
    MemberAddressForm,
    MemberDetailsForm,
    UserCreateForm,
    UserEditForm,
    ChangePasswordForm
)


class HttpResponseUnauthorized(HttpResponse):
    status_code = 401


class LoginRequiredMixin(object):
    """Add this to a class-based view to reject all non-authenticated users"""
    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated():
            return super(LoginRequiredMixin, self).dispatch(request,
                                                            *args,
                                                            **kwargs)

        if request.is_ajax():
            return HttpResponseUnauthorized('You must be logged in to perform this operation.')
        return redirect_to_login(request.get_full_path(), settings.LOGIN_URL)


class ViewUserProfile(TemplateView):
    template_name = 'users/profile.html'
    
    def get(self, request, *args, **kwargs):
        if int(kwargs['user_id']) is request.user.id:
            return redirect(reverse('users:profile'))
        
        return super(ViewUserProfile, self).get(request, *args, **kwargs)
    
    def get_context_data(self, **kwargs):
        context = super(ViewUserProfile, self).get_context_data(**kwargs)
        
        u_id = int(kwargs['user_id'])
        
        user = get_object_or_404(User, id=u_id)
        member = get_object_or_404(Member, user=user)
        
        context['form'] = UserEditForm(instance=user)
        context['userobj'] = user
        context['userpledges'] = Project.objects.filter(
            project_pledges__pledged_users__user_id=u_id)
        
        return context


class EditUserProfile(LoginRequiredMixin, TemplateView):
    form_class = UserEditForm
    template_name = 'users/profile.html'
    
    def post(self, request, *args, **kwargs):
        user = get_object_or_404(User, id=self.request.user.id)
        member = get_object_or_404(Member, user=user)        

        user_edit_form = UserEditForm(data=request.POST, instance=user)
        password_edit_form = ChangePasswordForm(data=request.POST, user=user, initial={})
        member_edit_form = MemberDetailsForm(data=request.POST, instance=member)

        if user_edit_form.is_valid():
            user_edit_form.save()
            
        if password_edit_form.has_changed():
            if password_edit_form.is_valid():
                password_edit_form.save()
                return redirect(reverse('users:login'))
            
        if member_edit_form.is_valid():
            member_edit_form.save()
            
        context = self.get_context_data(**kwargs)
        
        context['form'] = user_edit_form
        context['form2'] = password_edit_form
        context['form3'] = member_edit_form
        
        return render_to_response(self.template_name, context, context_instance=RequestContext(request))
    
    def get_context_data(self, **kwargs):
        context = super(EditUserProfile, self).get_context_data(**kwargs)

        user = get_object_or_404(User, id=self.request.user.id)
        member = get_object_or_404(Member, user=user)

        context['form'] = UserEditForm(instance=user)
        context['form2'] = ChangePasswordForm(user=user, initial={})
        context['form3'] = MemberDetailsForm(instance=member)
        context['user_addresses'] = get_list_or_404(Address, resident=user, active=True)
        context['userobj'] = user
        context['projects'] = Project.objects.filter(project_pledges__pledged_users__user_id=user.id)
        context['userpledges'] = UserPledge.objects.filter(user=user)
        
        return context


class CreateAddressView(LoginRequiredMixin, CreateView):
    form_class = MemberAddressForm
    model = Address
    template_name = 'users/edit-address.html'
    
    def post(self, request, *args, **kwargs):
        user_address_form = MemberAddressForm(data=request.POST)
        if user_address_form.is_valid():
            saved_address = user_address_form.save(commit=False)
            saved_address.resident = request.user
            saved_address.active = True
            saved_address.save()
            
            return redirect(reverse('users:edit_address', kwargs={'address_id': saved_address.id}))
        return super(CreateAddressView, self).post(request, *args, **kwargs)
    
    def get_context_data(self, **kwargs):
        context = super(CreateAddressView, self).get_context_data(**kwargs)
        context['user_addresses'] = get_list_or_404(Address, resident=self.request.user, active=True)
        
        return context

class EditAddressView(LoginRequiredMixin, UpdateView):
    form_class = MemberAddressForm
    model = Address
    template_name = 'users/edit-address.html'
    pk_url_kwarg = 'address_id'
    
    def get_queryset(self):
        return Address.objects.filter(active=True, resident=self.request.user)
    
    def get_context_data(self, **kwargs):
        context = super(EditAddressView, self).get_context_data(**kwargs)
        context['user_addresses'] = get_list_or_404(Address, resident=self.request.user, active=True)
        context['user_address'] = self.get_object()
        
        return context
    
    def get_success_url(self):
        return reverse('users:edit_address', kwargs={'address_id': self.get_object().id})


class DeleteAddressView(LoginRequiredMixin, RedirectView):
    permanent = False
    
    def get(self, request, *args, **kwargs):
        address_id = kwargs['address_id']
        address = get_object_or_404(Address, id=address_id, active=True)
        
        if address.resident == request.user:
            address.active = False
            address.save()        
        return super(DeleteAddressView, self).get(request, *args, **kwargs)

    def get_redirect_url(self, *args, **kwargs):
        return reverse('users:add_address')

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
