from django import forms
from .models import Project, Reward, Pledge


class ProjectEditCreateForm(forms.ModelForm):
    image = forms.ImageField(widget=forms.FileInput)

    class Meta:
        model = Project
        exclude = ('owner', 'status')


class RewardEditAddForm(forms.ModelForm):
    class Meta:
        model = Reward
        exclude = ('project',)


class PledgeEditAddForm(forms.ModelForm):

    def __init__(self, current_project, *args, **kwargs):
        super(PledgeEditAddForm, self).__init__(*args, **kwargs)
        self.fields['rewards'].queryset = Reward.objects.filter(
            project__id=current_project)

    class Meta:
        model = Pledge
        exclude = ('project',)

        widgets = {
            'rewards': forms.CheckboxSelectMultiple()
        }
