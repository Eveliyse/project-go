from django.shortcuts import get_object_or_404, render, render_to_response, redirect
from django.template import RequestContext
from django.http import HttpResponse, HttpResponseForbidden
from django.contrib.auth.models import User
from .models import Project, Status, Pledge, Reward, Category, UserPledge
from projects.forms import ProjectEditCreateForm, RewardEditAddForm, PledgeEditAddForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import redirect_to_login
from django.core.urlresolvers import reverse, reverse_lazy
from django.views.generic import CreateView, TemplateView, RedirectView, DetailView, ListView
from django.conf import settings
from django.db.models import Count, Sum, Avg, F, Q
from django.db.models.functions import Coalesce
from decimal import *
from django.utils import timezone

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
    
        newest_1=Project.objects.filter(status=open_status).order_by('-open_date')[:5]
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
            .order_by('-current_pledged')[:5]        
        
        context['newest_5'] = newest_5
        context['most_pledged_5'] = percent_pledged_5
        
        return context    

class ManageProjectsView(LoginRequiredMixin, TemplateView):
    template_name = 'projects/manage.html'

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super(ManageProjectsView, self).get_context_data(**kwargs)
        
        new_status = Status.objects.get(status = "New")
        open_status = Status.objects.get(status = "Open")
        closed_status = Status.objects.get(status = "Closed")         
        
        user_projects=Project.objects.filter(owner=self.request.user)
        up_amount_sum=user_projects.annotate(
                            current_pledged=Coalesce(
                                Sum('project_pledges__pledged_users__pledge__amount'),0.00))
        up_sum_percent=up_amount_sum.annotate(
                            current_percent=Coalesce(
                                (F('current_pledged')*100.00)/F('goal'),0))        
        
        up_sum_percent_new=up_sum_percent.filter(status=new_status)
        up_sum_percent_open=up_sum_percent.filter(status=open_status)
        up_sum_percent_closed=up_sum_percent.filter(status=closed_status)
        
        context['user_projects'] = up_sum_percent
        context['user_projects_new'] = up_sum_percent_new
        context['user_projects_open'] = up_sum_percent_open
        context['user_projects_closed'] = up_sum_percent_closed
        
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
    if project_id:
        p = get_object_or_404(Project, pk=project_id)
        if p.owner != request.user or p.status != Status.objects.get(status = "New"):
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
        'pledgerewards' : Pledge.objects.filter(project__id = project_id).order_by('amount'),
        'project': p}, context_instance=RequestContext(request))

@login_required
def EditAddPledgeRewards(request, project_id=None, mode=None, P_R_id=None):
    if project_id:
        project = get_object_or_404(Project, pk=project_id)
        if project.owner != request.user or project.status != Status.objects.get(status = "New"):
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
            'pledges' : Pledge.objects.filter(project__id = project_id).order_by('amount'),
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
            'pledges' : Pledge.objects.filter(project__id = project_id).order_by('amount'),
            'rewards' : Reward.objects.filter(project__id = project_id) ,
            'project': project}, context_instance=RequestContext(request))  
    else:
        pledge_edit_form = PledgeEditAddForm(initial={}, current_project = project_id)
        reward_edit_form = RewardEditAddForm(initial={})
    return render_to_response('projects/pledgerewards.html', {
        'form2': pledge_edit_form,
        'form3': reward_edit_form,
        'pledges' : Pledge.objects.filter(project__id = project_id).order_by('amount'),
        'rewards' : Reward.objects.filter(project__id = project_id) ,
        'project': project}, context_instance=RequestContext(request))


class DeletePledgeRewardsView(LoginRequiredMixin, RedirectView):
    permanent = False
    
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
    permanent = False
    
    def get(self,request, *args, **kwargs):
        project_id = kwargs['project_id']
        project = get_object_or_404(Project, pk=project_id)
        
        if project.owner == self.request.user:  
            new_status = get_object_or_404(Status, status = "New")
            open_status = get_object_or_404(Status, status = "Open")
            closed_status = get_object_or_404(Status, status = "Closed")
        
            if project.status.id == new_status.id:
                project.status = open_status
                project.open_date = timezone.now()
                project.save()
            elif project.status == open_status:
                project.status = closed_status
                project.save()  
            #sanity check?
            elif project.status == closed_status:
                project.status = closed_status
                project.save()       
        return super(UpdateStatusView,self).get(request, *args, **kwargs)
                
    def get_redirect_url(self, *args, **kwargs):
        return reverse('projects:manage')

class ProjectDetailsView(DetailView):
    model = Project
    pk_url_kwarg = 'project_id'
    
    def get(self, request, *args, **kwargs):
        self.pledge_added = None
        self.pledged = None
        
        project = get_object_or_404(Project, pk = kwargs['project_id'])
        
        if project.status == Status.objects.get(status = "New") and project.owner.id != self.request.user.id:
            return redirect(reverse('projects:index')) 
        
        match_user_pledges = UserPledge.objects.filter(user_id = request.user.id, pledge__project_id=kwargs['project_id'])
        if match_user_pledges:
            self.pledged = True
  
        if 'pledge_id' in kwargs:
            pledge_id = kwargs['pledge_id']
            pledge_obj = get_object_or_404(Pledge, pk=pledge_id)
    
            open_status = get_object_or_404(Status, status = "Open")
    
            if pledge_obj.project.status == open_status and pledge_obj.project.owner.id != self.request.user.id :
                if not match_user_pledges:
                    userpledge = UserPledge(user = request.user, pledge = pledge_obj)
                    userpledge.save()
                else:
                    userpledge = UserPledge.objects.get(user = request.user, pledge__project_id=kwargs['project_id'])
                    userpledge.pledge = pledge_obj
                    userpledge.save()
                self.pledge_added = True
            else:
                self.pledge_added = False

            return redirect(reverse('projects:details', kwargs={'project_id':kwargs['project_id']}))
        return super(ProjectDetailsView,self).get(request, *args, **kwargs)    
    
    def get_context_data(self, **kwargs):
        context = super(ProjectDetailsView, self).get_context_data(**kwargs)
        pledgerewards = Pledge.objects.filter(project_id = self.kwargs['project_id'])
        pledgerewards_count = pledgerewards.annotate(count=Count('pledged_users__pledge_id')).order_by('amount')
        
        pledgers = User.objects.filter(user_pledges__pledge__project_id = self.kwargs['project_id'])
        
        context['pledgerewards'] = pledgerewards_count
        context['pledgers'] = pledgers

        if self.pledge_added is True:
            context['pledge_added'] = 'PLEDGE ADDED'
        elif self.pledge_added is False:
            context['pledge_added'] = 'NOOO FAIL BOOO'       
            
        if self.pledged is True:
            up = UserPledge.objects.get(user_id = self.request.user.id, pledge__project_id=self.kwargs['project_id'])
            context['pledge'] = Pledge.objects.get(id = up.pledge.id)
        
        return context    

class ProjectListView(ListView):
    model = Project   
    context_object_name = 'project_list'

    def get(self, request, *args, **kwargs):
        if 'search_term' in request.GET:
            search_term = self.request.GET['search_term']
            if search_term is not None and len(search_term) > 0:
                new_status=Status.objects.get(status="New")
                search_term_list = search_term.split()
                
                search_results =  Project.objects.filter(
                                                    reduce(
                                                        lambda x, y: x | y, [
                                                            Q(title__contains=word) for word in search_term_list]
                                                        )
                                                    ).exclude(status = new_status).order_by('status')
                if search_results:
                    self.queryset = search_results
                else:
                    self.queryset = Project.objects.none()
        return super(ProjectListView,self).get(request, *args, **kwargs)
        
    def get_queryset(self):
        new_status=Status.objects.get(status="New")
        if 'category_id' in self.kwargs and self.kwargs['category_id'] is not None:
            get_object_or_404(Category, id = self.kwargs['category_id'])
            
            return Project.objects.filter(category_id = self.kwargs['category_id']).exclude(status = new_status).order_by('status')
        elif 'search_term' in self.request.GET:
            search_term = self.request.GET['search_term']
            if search_term is None or len(search_term) <= 0:
                return Project.objects.exclude(status = new_status).order_by('status')
        else:
            return Project.objects.exclude(status = new_status).order_by('status')
        return super(ProjectListView,self).get_queryset()
    
    def get_context_data(self, **kwargs):
        context = super(ProjectListView, self).get_context_data(**kwargs)
        
        if 'category_id' in self.kwargs and self.kwargs['category_id'] is not None:
            context['cat_name'] = get_object_or_404(Category, id = self.kwargs['category_id']).category
        elif 'search_term' in self.request.GET:
            search_term = self.request.GET['search_term']
            if search_term is not None and len(search_term) > 0:        
                context['search_term'] = search_term
        return context