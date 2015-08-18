from django.shortcuts import get_object_or_404, render, render_to_response, redirect
from django.template import RequestContext
from django.http import HttpResponse, HttpResponseForbidden
from django.contrib.auth.models import User
from .models import Project, Status, Pledge, Reward
from projects.forms import ProjectEditCreateForm, RewardEditAddForm, PledgeEditAddForm

#placeholder for now
def index(request):
    return render(request, 'projects/manage.html')

@login_required
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

@login_required
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

@login_required
def pledgerewards(request, project_id=None, mode=None, P_R_id=None):
    if project_id:
        project = get_object_or_404(Project, pk=project_id)
        if project.owner != request.user:
            return HttpResponseForbidden()
    else:
        return redirect('/projects/create')
    
    pledges = Pledge.objects.filter(project__id = project_id)
    rewards = Reward.objects.filter(project__id = project_id)    
    
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
            #if 'reward' in request.POST:
            reward_edit_form = RewardEditAddForm(data=request.POST)
            if reward_edit_form.has_changed():
                if reward_edit_form.is_valid():
                    r = reward_edit_form.save(commit = False)
                    r.project = Project.objects.get(id = project_id)
                    r.save()

            #if 'pledge' in request.POST:
            pledge_edit_form = PledgeEditAddForm(data=request.POST, current_project = project_id)
            if pledge_edit_form.has_changed():
                if pledge_edit_form.is_valid():
                    p = pledge_edit_form.save(commit = False)
                    p.project = Project.objects.get(id = project_id)
                    p.save()
                    pledge_edit_form.save_m2m()
       
    if mode == "pledge" and P_R_id is not None:
        p_instance = Pledge.objects.get(id = P_R_id)
        pledge_edit_form = PledgeEditAddForm(current_project=project_id, instance=p_instance)
        reward_edit_form = RewardEditAddForm()
        return render_to_response('projects/pledgerewards.html', {
            'form2': pledge_edit_form,
            'form3': reward_edit_form,
            'mode': mode,
            'instance':p_instance,
            'pledges' : pledges,
            'rewards' : rewards,
            'project': project}, context_instance=RequestContext(request))  
    elif mode == "reward" and P_R_id is not None:
        r_instance = Reward.objects.get(id = P_R_id)
        pledge_edit_form = PledgeEditAddForm(initial={}, current_project=project_id)
        reward_edit_form = RewardEditAddForm(initial={}, instance=r_instance)
        return render_to_response('projects/pledgerewards.html', {
            'form2': pledge_edit_form,
            'form3': reward_edit_form,
            'mode': mode,
            'instance':r_instance,
            'pledges' : pledges,
            'rewards' : rewards,
            'project': project}, context_instance=RequestContext(request))  
    else:
        pledge_edit_form = PledgeEditAddForm(initial={}, current_project = project_id)
        reward_edit_form = RewardEditAddForm(initial={})
    return render_to_response('projects/pledgerewards.html', {
        'form2': pledge_edit_form,
        'form3': reward_edit_form,
        'pledges' : pledges,
        'rewards' : rewards,
        'project': project}, context_instance=RequestContext(request))

@login_required
def delete(request):
    return render(request, 'projects/details.html')

def details(request):
    return render(request, 'projects/details.html')