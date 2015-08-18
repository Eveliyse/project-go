from django.shortcuts import get_object_or_404, render, render_to_response, redirect
from django.template import RequestContext
from django.http import HttpResponse, HttpResponseForbidden
from django.contrib.auth.models import User
from .models import Project, Status, Pledge, Reward
from projects.forms import ProjectEditCreateForm, RewardEditAddForm, PledgeEditAddForm

#placeholder for now
def index(request):
    return render(request, 'projects/manage.html')

def create(request):
    """ If POST then process form and create project entry
        Otherwise, create form and display
    """    
    if request.method == "POST":
        project_create_form = ProjectEditCreateForm(data=request.POST, files=request.FILES, prefix="project")
        if project_create_form.is_valid():
            p = project_create_form.save(commit = False)
            p.owner = request.user
            p.save()
            return redirect('/projects/edit/' + str(p.id))
    else:
        project_create_form = ProjectEditCreateForm(prefix="project")
    return render_to_response('projects/editcreate.html', {
        'form': project_create_form,
        }, context_instance=RequestContext(request))

def edit(request, project_id=None):
    if project_id:
        p = get_object_or_404(Project, pk=project_id)
        if p.owner != request.user:
            return HttpResponseForbidden()
    else:
        return redirect('/projects/create')
    
    if request.POST:
        if 'project' in request.POST:
            project_edit_form = ProjectEditCreateForm(data=request.POST, files=request.FILES, instance=p, prefix="project")
            if project_edit_form.is_valid():
                project_edit_form.save()
                
        #if 'reward' in request.POST:
        #    reward_edit_form = RewardEditAddForm(data=request.POST, initial={}, prefix="reward")
        #    if reward_edit_form.has_changed():
        #        if reward_edit_form.is_valid():
        #            r = reward_edit_form.save(commit = False)
        #            r.project = Project.objects.get(id = project_id)
        #            r.save()
       # 
       # if 'pledge' in request.POST:
       #     pledge_edit_form = PledgeEditAddForm(data=request.POST, initial={}, prefix="pledge", current_project = project_id)
       #     if pledge_edit_form.has_changed():
       #         if pledge_edit_form.is_valid():
       #             p = pledge_edit_form.save(commit = False)
       #             p.project = Project.objects.get(id = project_id)
       #             p.save()
       #             pledge_edit_form.save_m2m()
                    
    project_edit_form = ProjectEditCreateForm(instance=p, prefix="project")
    #pledge_edit_form = PledgeEditAddForm(initial={}, prefix="pledge", current_project = project_id)
    #reward_edit_form = RewardEditAddForm(initial={}, prefix="reward")
    return render_to_response('projects/editcreate.html', {
        'form': project_edit_form,
        #'form2': pledge_edit_form,
        #'form3': reward_edit_form,
        'pledges' : Pledge.objects.filter(project__id = project_id),
        'rewards' : Reward.objects.filter(project__id = project_id),
        'project': p}, context_instance=RequestContext(request))

def pledgerewards(request, project_id=None):
    if project_id:
        project = get_object_or_404(Project, pk=project_id)
        if project.owner != request.user:
            return HttpResponseForbidden()
    else:
        return redirect('/projects/create')
    
    if request.POST:
                
        #if 'reward' in request.POST:
            reward_edit_form = RewardEditAddForm(data=request.POST, initial={}, prefix="reward")
            if reward_edit_form.has_changed():
                if reward_edit_form.is_valid():
                    r = reward_edit_form.save(commit = False)
                    r.project = Project.objects.get(id = project_id)
                    r.save()
        
        #if 'pledge' in request.POST:
            pledge_edit_form = PledgeEditAddForm(data=request.POST, initial={}, prefix="pledge", current_project = project_id)
            if pledge_edit_form.has_changed():
                if pledge_edit_form.is_valid():
                    p = pledge_edit_form.save(commit = False)
                    p.project = Project.objects.get(id = project_id)
                    p.save()
                    pledge_edit_form.save_m2m()
                    
    pledge_edit_form = PledgeEditAddForm(initial={}, prefix="pledge", current_project = project_id)
    reward_edit_form = RewardEditAddForm(initial={}, prefix="reward")
    pledges = Pledge.objects.filter(project__id = project_id)
    rewards = Reward.objects.filter(project__id = project_id)
    return render_to_response('projects/pledgerewards.html', {
        'form2': pledge_edit_form,
        'form3': reward_edit_form,
        'pledges' : pledges,
        'rewards' : rewards,
        'project': project}, context_instance=RequestContext(request))

def details(request):
    return render(request, 'projects/details.html')