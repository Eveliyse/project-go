from django.shortcuts import get_object_or_404, render, render_to_response, redirect
from django.template import RequestContext
from django.http import HttpResponse, HttpResponseForbidden
from django.contrib.auth.models import User
from .models import Project, Status
from projects.forms import ProjectEditCreateForm

def index(request):
    return render(request, 'projects/manage.html')

def create(request):
    if request.method == "POST":
        project_create_form = ProjectEditCreateForm(data=request.POST, files=request.FILES, prefix="project")
        if project_create_form.is_valid():
            p = project_create_form.save(commit=False)
            p.owner = request.user
            p.status = Status.objects.get(status = "New")
            p.save()
            return redirect('/projects/edit/' + p.id)
    else:
        project_create_form = ProjectEditCreateForm(prefix="project")
    return render_to_response('projects/editcreate.html', {
        'form': project_create_form,
        }, context_instance=RequestContext(request))

def edit(request, id=None):
    if id:
        p = get_object_or_404(Project, pk=id)
        if p.owner != request.user:
            return HttpResponseForbidden()
    else:
        return redirect('/projects/create')

    if request.POST:
        project_edit_form = ProjectEditCreateForm(data=request.POST, files=request.FILES, instance=p)
        if project_edit_form.is_valid():
            project_edit_form.save()
    else:
        project_edit_form = ProjectEditCreateForm(instance=p)
    return render_to_response('projects/editcreate.html', {
        'form': project_edit_form,
        'project': p}, context_instance=RequestContext(request))

def details(request):
    return render(request, 'projects/details.html')