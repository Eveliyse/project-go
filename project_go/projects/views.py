from django.shortcuts import get_object_or_404, render, render_to_response, redirect
from django.template import RequestContext
from django.http import HttpResponse, HttpResponseForbidden
from django.contrib.auth.models import User
from .models import Project, Status, Pledge, Reward
from projects.forms import ProjectEditCreateForm, RewardEditAddForm, PledgeEditAddForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import redirect_to_login
from django.core.urlresolvers import reverse, reverse_lazy
from django.views.generic import CreateView, TemplateView, RedirectView, DetailView
from django.conf import settings
from django.db.models import Count, Sum, Avg, F
from django.db.models.functions import Coalesce
from decimal import *

class LoginRequiredMixin(object):
    """Add this to a class-based view to reject all non-authenticated users"""
    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated():
            return super(LoginRequiredMixin, self).dispatch(request, *args, **kwargs)

        if request.is_ajax():
            return HttpResponseUnauthorized('You must be logged in to perform this operation.')
        return redirect_to_login(request.get_full_path(), settings.LOGIN_URL)


class IndexView(TemplateView):
    template_name = 'projects/index.html'
    
    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super(IndexView, self).get_context_data(**kwargs)

        open_status=Status.objects.get(status="Open")
    
        newest_1=Project.objects.filter(status=open_status).order_by('created_date')[:5]
        newest_2=newest_1.annotate(
            current_pledged=Coalesce(
                Sum('project_pledges__pledged_users__pledge__amount'),0.00))
        newest_5=newest_2.annotate(
            current_percent=Coalesce(
                (F('current_pledged')*100.00)/F('goal'),0))
    
    
        open_projects=Project.objects.filter(status=open_status)
        sum_pledged_5=open_projects.annotate(
            current_pledged=Coalesce(
                Sum('project_pledges__pledged_users__pledge__amount'),0.00))
        percent_pledged_5=sum_pledged_5.annotate(
            current_percent=Coalesce(
                (F('current_pledged')*100.00)/F('goal'),0)) \
            .order_by('-current_percent')[:5]        
        
        context['newest_5'] = newest_5
        context['most_pledged_5'] = percent_pledged_5
        
        return context    

class ManageProjectsView(LoginRequiredMixin, TemplateView):
    template_name = 'projects/manage.html'

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super(ManageProjectsView, self).get_context_data(**kwargs)
        
        newest_1=Project.objects.filter(owner=self.request.user).order_by('created_date')[:5]
        newest_2=newest_1.annotate(
                            current_pledged=Coalesce(
                                Sum('project_pledges__pledged_users__pledge__amount'),0.00))
        newest_5=newest_2.annotate(
                            current_percent=Coalesce(
                                (F('current_pledged')*100.00)/F('goal'),0))        
        
        context['user_projects'] = newest_5
        return context

class CreateProjectView(LoginRequiredMixin, CreateView):
    """ If POST then process form and create project entry
        Otherwise, create form and display
    """    
    form_class = ProjectEditCreateForm     
    model = Project
    template_name = 'projects/edit_create.html'
    
    def post(self, request, *args, **kwargs):
        project_create_form = ProjectEditCreateForm(data=request.POST, files=request.FILES)
        if project_create_form.is_valid():
            p = project_create_form.save(commit = False)
            p.owner = request.user
            p.status = Status.objects.get(status = "New")
            p.save()
            return redirect(reverse('projects:edit', kwargs={'project_id':p.id}))
        return render_to_response('projects/edit_create.html', {
            'form': project_create_form,
            }, context_instance=RequestContext(request))
        

@login_required
def Edit(request, project_id=None):
    #TODO edit only if NEW
    if project_id:
        p = get_object_or_404(Project, pk=project_id)
        if p.owner != request.user:
            return redirect(reverse('projects:manage'))
    else:
        return redirect(reverse('projects:create'))
    
    if request.POST:
        if 'project' in request.POST:
            project_edit_form = ProjectEditCreateForm(data=request.POST, files=request.FILES, instance=p, prefix="project")
            if project_edit_form.is_valid():
                project_edit_form.save()
                
    project_edit_form = ProjectEditCreateForm(instance=p, prefix="project")
    return render_to_response('projects/edit_create.html', {
        'form': project_edit_form,
        'pledges' : Pledge.objects.filter(project__id = project_id),
        'project': p}, context_instance=RequestContext(request))

@login_required
def EditAddPledgeRewards(request, project_id=None, mode=None, P_R_id=None):
    #TODO edit only if NEW
    if project_id:
        project = get_object_or_404(Project, pk=project_id)
        if project.owner != request.user:
            return redirect(reverse('projects:manage')) 
    else:
        return redirect(reverse('projects:manage')) 
    
    if request.POST:
        if mode == "pledge" and P_R_id is not None:
            p_instance = get_object_or_404(Pledge, id = P_R_id)
            pledge_edit_form = PledgeEditAddForm(data=request.POST, instance=p_instance, current_project=project_id)
            if pledge_edit_form.has_changed():
                if pledge_edit_form.is_valid():
                    p = pledge_edit_form.save(commit = False)
                    p.project = Project.objects.get(id = project_id)
                    p.save()
                    pledge_edit_form.save_m2m()    
        elif mode == "reward" and P_R_id is not None:
            r_instance = get_object_or_404(Reward, id = P_R_id)
            reward_edit_form = RewardEditAddForm(data=request.POST, instance=r_instance)
            if reward_edit_form.has_changed():
                if reward_edit_form.is_valid():
                    r = reward_edit_form.save(commit = False)
                    r.project = Project.objects.get(id = project_id)
                    r.save()       
        else:
            reward_edit_form = RewardEditAddForm(data=request.POST)
            if reward_edit_form.has_changed():
                if reward_edit_form.is_valid():
                    r = reward_edit_form.save(commit = False)
                    r.project = Project.objects.get(id = project_id)
                    r.save()

            pledge_edit_form = PledgeEditAddForm(data=request.POST, current_project = project_id)
            if pledge_edit_form.has_changed():
                if pledge_edit_form.is_valid():
                    p = pledge_edit_form.save(commit = False)
                    p.project = Project.objects.get(id = project_id)
                    p.save()
                    pledge_edit_form.save_m2m()
       
    if mode == "pledge" and P_R_id is not None:
        p_instance = get_object_or_404(Pledge, id = P_R_id)
        if p_instance.project.owner != request.user:
            return redirect(reverse('projects:manage')) 
        pledge_edit_form = PledgeEditAddForm(current_project=project_id, instance=p_instance)
        reward_edit_form = RewardEditAddForm()
        return render_to_response('projects/pledgerewards.html', {
            'form2': pledge_edit_form,
            'form3': reward_edit_form,
            'mode': mode,
            'instance':p_instance,
            'pledges' : Pledge.objects.filter(project__id = project_id),
            'rewards' : Reward.objects.filter(project__id = project_id) ,
            'project': project}, context_instance=RequestContext(request))  
    elif mode == "reward" and P_R_id is not None:
        r_instance = get_object_or_404(Reward, id = P_R_id)
        if r_instance.project.owner != request.user:
            return redirect(reverse('projects:manage'))         
        pledge_edit_form = PledgeEditAddForm(initial={}, current_project=project_id)
        reward_edit_form = RewardEditAddForm(initial={}, instance=r_instance)
        return render_to_response('projects/pledgerewards.html', {
            'form2': pledge_edit_form,
            'form3': reward_edit_form,
            'mode': mode,
            'instance':r_instance,
            'pledges' : Pledge.objects.filter(project__id = project_id),
            'rewards' : Reward.objects.filter(project__id = project_id) ,
            'project': project}, context_instance=RequestContext(request))  
    else:
        pledge_edit_form = PledgeEditAddForm(initial={}, current_project = project_id)
        reward_edit_form = RewardEditAddForm(initial={})
    return render_to_response('projects/pledgerewards.html', {
        'form2': pledge_edit_form,
        'form3': reward_edit_form,
        'pledges' : Pledge.objects.filter(project__id = project_id),
        'rewards' : Reward.objects.filter(project__id = project_id) ,
        'project': project}, context_instance=RequestContext(request))


class DeletePledgeRewardsView(LoginRequiredMixin, RedirectView):
    def get_redirect_url(self, *args, **kwargs):
        project_id = kwargs['project_id']
        mode = kwargs['mode']
        P_R_id = kwargs['P_R_id']
        
        if mode == "pledge":
            obj = get_object_or_404(Pledge, pk=P_R_id)
        elif mode == "reward":
            obj = get_object_or_404(Reward, pk=P_R_id)
            
        if obj.project.owner != self.request.user:
            return reverse('projects:manage')   
    
        obj.delete()
        return reverse('projects:pledgerewards', kwargs={'project_id':project_id})


class UpdateStatusView(LoginRequiredMixin, RedirectView):
    pattern_name = 'manage'
    permanent = False
    
    def get(self, *args, **kwargs):
        project_id = kwargs['project_id']
        project = get_object_or_404(Project, pk=project_id)
        
        if project.owner == self.request.user:  
            new_status = get_object_or_404(Status, status = "New")
            open_status = get_object_or_404(Status, status = "Open")
            closed_status = get_object_or_404(Status, status = "Closed")
        
            if project.status.id == new_status.id:
                project.status = open_status
                project.save()
            elif project.status == open_status:
                project.status = closed_status
                project.save()  
            #sanity check?
            elif project.status == closed_status:
                project.status = new_status
                project.save()       
        return super(UpdateStatusView,self).get(*args, **kwargs)
                
    def get_redirect_url(self, *args, **kwargs):
        return reverse('projects:manage')

class ProjectDetailsView(DetailView):
    model = Project
    
    def get_context_data(self, **kwargs):
        context = super(ProjectDetailsView, self).get_context_data(**kwargs)
        pledgerewards = Pledge.objects.filter(project_id = self.kwargs['pk'])
        pledgerewards_count = pledgerewards.annotate(count=Count('pledged_users__pledge_id'))
        
        pledgers = User.objects.filter(user_pledges__pledge__project_id = self.kwargs['pk'])
        
        context['pledgerewards'] = pledgerewards_count
        context['pledgers'] = pledgers
        return context    
    