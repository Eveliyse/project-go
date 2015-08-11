from django.shortcuts import render, render_to_response, redirect
from django.template import RequestContext
from django.http import HttpResponse
from django.shortcuts import HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login as django_login, authenticate, logout as django_logout
from django.contrib.auth.forms import AuthenticationForm

@login_required
def index(request):
    return render(request, 'users/index.html')

def login(request):
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
        
        #return render(request, 'users/login.html')
    else:
        return HttpResponseRedirect('/users/')    

def logout(request):
    django_logout(request)
    # Redirect to a success page.
    #return HttpResponse("Logout")
    return HttpResponseRedirect('/users/')