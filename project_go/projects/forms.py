from django import forms
from django.forms.extras.widgets import SelectDateWidget
from .models import Project
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
import datetime

class ProjectCreateForm(forms.ModelForm):
    image = forms.ImageField(widget=forms.FileInput)
    class Meta:
        model = Project
        exclude = ('owner','status')      
    
    