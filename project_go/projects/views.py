from django.shortcuts import get_object_or_404, render_to_response, redirect
from django.template import RequestContext
from django.http import HttpResponse
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import redirect_to_login
from django.core.urlresolvers import reverse
from django.views.generic import (
    CreateView,
    TemplateView,
    RedirectView,
    DetailView,
    ListView
)
from django.conf import settings
from django.db.models import Count, Sum, F, Q
from django.db.models.functions import Coalesce
from django.utils import timezone

from .models import Project, Status, Pledge, Reward, Category, UserPledge

from projects.forms import (
    ProjectEditCreateForm,
    RewardEditAddForm,
    PledgeEditAddForm
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


class IndexView(TemplateView):
    template_name = 'projects/index.html'

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super(IndexView, self).get_context_data(**kwargs)

        open_status = Status.objects.get(status="Open")

        # Getting set of newest open projects and adding extra columns
        newest_projects = (Project.objects.filter(status=open_status).order_by('-open_date')[:6])

        newest_projects_amount = newest_projects.annotate(
            current_pledged=Coalesce(
                Sum('project_pledges__pledged_users__pledge__amount'), 0.00))

        newest_projects_amount_percent = newest_projects_amount.annotate(
            current_percent=Coalesce(
                (F('current_pledged') * 100.00) / F('goal'), 0))

        # Getting set of most funded open projects and adding extra columns
        open_projects = Project.objects.filter(status=open_status)

        sum_pledged_5 = open_projects.annotate(
            current_pledged=Coalesce(
                Sum('project_pledges__pledged_users__pledge__amount'), 0.00))

        percent_pledged_5 = (
            sum_pledged_5.annotate(current_percent=Coalesce(
                (F('current_pledged') * 100.00) / F('goal'), 0)).order_by('-current_pledged')[:6])

        # adding sets to context
        context['newest_5'] = newest_projects_amount_percent
        context['most_pledged_5'] = percent_pledged_5

        return context


class ManageProjectsView(LoginRequiredMixin, TemplateView):
    template_name = 'projects/manage.html'

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super(ManageProjectsView, self).get_context_data(**kwargs)

        new_status = Status.objects.get(status="New")
        open_status = Status.objects.get(status="Open")
        closed_status = Status.objects.get(status="Closed")

        user_projects = Project.objects.filter(owner=self.request.user)
        up_amount_sum = user_projects.annotate(
            current_pledged=Coalesce(
                Sum('project_pledges__pledged_users__pledge__amount'), 0.00))

        up_sum_percent = up_amount_sum.annotate(
            current_percent=Coalesce(
                (F('current_pledged') * 100.00) / F('goal'), 0))

        up_sum_percent_new = up_sum_percent.filter(status=new_status)
        up_sum_percent_open = up_sum_percent.filter(status=open_status)
        up_sum_percent_closed = up_sum_percent.filter(status=closed_status)

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
            p = project_create_form.save(commit=False)
            p.owner = request.user
            p.status = Status.objects.get(status="New")
            p.save()
            return redirect(reverse('projects:edit', kwargs={'project_id': p.id}))
        return render_to_response('projects/edit_create.html', {
            'form': project_create_form,
        }, context_instance=RequestContext(request))


@login_required
def Edit(request, project_id=None):
    if project_id:
        p = get_object_or_404(Project, pk=project_id)
        if (p.owner != request.user or
                p.status != Status.objects.get(status="New")):
            return redirect(reverse('projects:manage'))
    else:
        return redirect(reverse('projects:create'))

    if request.POST:
            project_edit_form = ProjectEditCreateForm(data=request.POST,
                                                      files=request.FILES,
                                                      instance=p)
            if project_edit_form.is_valid():
                project_edit_form.save()

    project_edit_form = ProjectEditCreateForm(instance=p)
    return render_to_response('projects/edit_create.html', {
        'form': project_edit_form,
        'pledgerewards': Pledge.objects.filter(project__id=project_id)
        .order_by('amount'),
        'project': p}, context_instance=RequestContext(request))


@login_required
def EditAddPledgeRewards(request, project_id=None, mode=None, P_R_id=None):
    if project_id:
        project = get_object_or_404(Project, pk=project_id)
        if (project.owner != request.user or project.status != Status.objects.get(status="New")):
            return redirect(reverse('projects:manage'))
    else:
        return redirect(reverse('projects:manage'))

    if request.POST:
        if mode == "pledge" and P_R_id is not None:
            p_instance = get_object_or_404(Pledge, id=P_R_id)
            pledge_edit_form = PledgeEditAddForm(data=request.POST,
                                                 instance=p_instance,
                                                 current_project=project_id)
            if pledge_edit_form.has_changed():
                if pledge_edit_form.is_valid():
                    p = pledge_edit_form.save(commit=False)
                    p.project = Project.objects.get(id=project_id)
                    p.save()
                    pledge_edit_form.save_m2m()
        elif mode == "reward" and P_R_id is not None:
            r_instance = get_object_or_404(Reward, id=P_R_id)
            reward_edit_form = RewardEditAddForm(data=request.POST,
                                                 instance=r_instance)
            if reward_edit_form.has_changed():
                if reward_edit_form.is_valid():
                    r = reward_edit_form.save(commit=False)
                    r.project = Project.objects.get(id=project_id)
                    r.save()
        else:
            reward_edit_form = RewardEditAddForm(data=request.POST)
            if reward_edit_form.has_changed():
                if reward_edit_form.is_valid():
                    r = reward_edit_form.save(commit=False)
                    r.project = Project.objects.get(id=project_id)
                    r.save()

            pledge_edit_form = PledgeEditAddForm(data=request.POST,
                                                 current_project=project_id)
            if pledge_edit_form.has_changed():
                if pledge_edit_form.is_valid():
                    p = pledge_edit_form.save(commit=False)
                    p.project = Project.objects.get(id=project_id)
                    p.save()
                    pledge_edit_form.save_m2m()

    if mode == "pledge" and P_R_id is not None:
        p_instance = get_object_or_404(Pledge, id=P_R_id)
        pledge_edit_form = PledgeEditAddForm(current_project=project_id,
                                             instance=p_instance)
        reward_edit_form = RewardEditAddForm()
        return render_to_response('projects/pledgerewards.html', {
            'form2': pledge_edit_form,
            'form3': reward_edit_form,
            'mode': mode,
            'instance': p_instance,
            'pledges': Pledge.objects.filter(project__id=project_id)
            .order_by('amount'),
            'rewards': Reward.objects.filter(project__id=project_id),
            'project': project}, context_instance=RequestContext(request))
    elif mode == "reward" and P_R_id is not None:
        r_instance = get_object_or_404(Reward, id=P_R_id)
        pledge_edit_form = PledgeEditAddForm(initial={},
                                             current_project=project_id)
        reward_edit_form = RewardEditAddForm(initial={}, instance=r_instance)
        return render_to_response('projects/pledgerewards.html', {
            'form2': pledge_edit_form,
            'form3': reward_edit_form,
            'mode': mode,
            'instance': r_instance,
            'pledges': Pledge.objects.filter(project__id=project_id)
            .order_by('amount'),
            'rewards': Reward.objects.filter(project__id=project_id),
            'project': project}, context_instance=RequestContext(request))
    else:
        pledge_edit_form = PledgeEditAddForm(initial={},
                                             current_project=project_id)
        reward_edit_form = RewardEditAddForm(initial={})
    return render_to_response('projects/pledgerewards.html', {
        'form2': pledge_edit_form,
        'form3': reward_edit_form,
        'pledges': Pledge.objects.filter(project__id=project_id)
        .order_by('amount'),
        'rewards': Reward.objects.filter(project__id=project_id),
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
        return reverse('projects:pledgerewards',
                       kwargs={'project_id': project_id})


class UpdateStatusView(LoginRequiredMixin, RedirectView):
    permanent = False

    def get(self, request, *args, **kwargs):
        project_id = kwargs['project_id']
        project = get_object_or_404(Project, pk=project_id)

        if project.owner == self.request.user:
            new_status = get_object_or_404(Status, status="New")
            open_status = get_object_or_404(Status, status="Open")
            closed_status = get_object_or_404(Status, status="Closed")

            if project.status.id == new_status.id:
                project.status = open_status
                project.open_date = timezone.now()
                project.save()
            elif project.status == open_status:
                project.status = closed_status
                project.save()
            # sanity check?
            elif project.status == closed_status:
                project.status = closed_status
                project.save()
        return super(UpdateStatusView, self).get(request, *args, **kwargs)

    def get_redirect_url(self, *args, **kwargs):
        return reverse('projects:manage')


class ProjectDetailsView(DetailView):
    model = Project
    pk_url_kwarg = 'project_id'

    def get(self, request, *args, **kwargs):
        #check if user is allowed to view page and if they have already pledged
        self.pledged = None

        project = get_object_or_404(Project, pk=kwargs['project_id'])

        if (project.status == Status.objects.get(status="New") and
                project.owner.id != self.request.user.id):
            return redirect(reverse('projects:index'))

        matched_user_pledge = UserPledge.objects.filter(user_id=request.user.id,
                                                       pledge__project_id=kwargs['project_id'])
        if matched_user_pledge:
            self.pledged = True

        return super(ProjectDetailsView, self).get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        #load in pledgerewards, list of user pledgers and viewer's pledge amount if applicable
        context = super(ProjectDetailsView, self).get_context_data(**kwargs)
        pledgerewards = Pledge.objects.filter(
            project_id=self.kwargs['project_id'])
        pledgerewards_count = pledgerewards.annotate(
            count=Count('pledged_users__pledge_id')).order_by('amount')

        pledgers = User.objects.filter(
            user_pledges__pledge__project_id=self.kwargs['project_id'])

        context['pledgerewards'] = pledgerewards_count
        context['pledgers'] = pledgers

        if self.pledged is True:
            up = UserPledge.objects.get(
                user_id=self.request.user.id,
                pledge__project_id=self.kwargs['project_id'])
            context['pledge'] = Pledge.objects.get(id=up.pledge.id)

        return context


class ProjectAddUserPledgeView(LoginRequiredMixin, RedirectView):
    permanent = False
    
    def get(self, request, *args, **kwargs):
        pledge_obj = get_object_or_404(Pledge, pk=kwargs['pledge_id'])

        open_status = get_object_or_404(Status, status="Open")

        if (pledge_obj.project.status == open_status and
            pledge_obj.project.owner.id != self.request.user.id):
            
            matched_user_pledge = UserPledge.objects.filter(user_id=request.user.id,
                                                           pledge__project_id=kwargs['project_id'])            

            if not matched_user_pledge:
                userpledge = UserPledge(user=request.user, pledge=pledge_obj)
                userpledge.save()
            else:
                userpledge = UserPledge.objects.get(user=request.user,
                                                    pledge__project_id=kwargs['project_id'])
                userpledge.pledge = pledge_obj
                userpledge.save()

        return redirect(reverse('projects:details', kwargs={'project_id': kwargs['project_id']}))    


class ProjectSearchListView(ListView):
    model = Project
    context_object_name = 'project_list'

    def get_queryset(self):
        new_status = Status.objects.get(status="New")
        
        if 'search_term' in self.request.GET:
            search_term = self.request.GET['search_term']
            if search_term is not None and len(search_term.replace(" ", "")) > 0:
                search_term_list = search_term.split()

                search_results = Project.objects.filter(
                    reduce(
                        lambda x, y: x | y, [
                            Q(title__contains=word)
                            for word in search_term_list]
                    )
                    ).exclude(status=new_status).order_by('status')
                if search_results:
                    return search_results
                else:
                    return Project.objects.none()
                
        return (Project.objects.exclude(status=new_status)
                .order_by('status'))

    def get_context_data(self, **kwargs):
        context = super(ProjectSearchListView, self).get_context_data(**kwargs)
        if 'search_term' in self.request.GET:
            search_term = self.request.GET['search_term']
            if search_term is not None and len(search_term) > 0:
                context['search_term'] = search_term

        return context


class ProjectCategoryListView(ListView):
    model = Project
    context_object_name = 'project_list'

    def get_queryset(self):
        new_status = Status.objects.get(status="New")
        
        get_object_or_404(Category, id=self.kwargs['category_id'])

        return (Project.objects.filter(category_id=self.kwargs['category_id'])
                .exclude(status=new_status).order_by('status'))

    def get_context_data(self, **kwargs):
        context = super(ProjectCategoryListView, self).get_context_data(**kwargs)
        
        context['cat_name'] = get_object_or_404(Category, id=self.kwargs['category_id']).category
        
        return context