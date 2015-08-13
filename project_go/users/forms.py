from django import forms
from django.forms.extras.widgets import SelectDateWidget
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from .models import Address, Member
import datetime

class MemberAddressForm(forms.ModelForm):

    class Meta:
        model = Address
        exclude = ['resident',]
        
class MemberDetailsForm(forms.ModelForm):
    dob = forms.DateField(widget=SelectDateWidget(years=range(datetime.datetime.now().year-15,datetime.datetime.now().year-100,-1)))
    
    class Meta:
        model = Member
        exclude = ['user',]
        
class UserEditForm(forms.ModelForm):
    first_name = forms.CharField(max_length=30)
    last_name = forms.CharField(max_length=30)
    email = forms.EmailField(max_length=75)
    
    class Meta:
        model = User
        fields = ("first_name", "last_name", "email", ) 

class UserCreateForm(UserCreationForm):
    first_name = forms.CharField(max_length=30)
    last_name = forms.CharField(max_length=30)
    email = forms.EmailField(max_length=75)
    username = forms.CharField(max_length=75)
    
    class Meta:
        model = User
        fields = ("username", "first_name", "last_name", "email",) 
        
    def save(self, commit=True):
        user = super(UserCreateForm, self).save(commit=False)
        user.first_name = self.cleaned_data["first_name"]
        user.last_name = self.cleaned_data["last_name"]
        user.email = self.cleaned_data["email"]
        if commit:
            user.save()
        return user

    