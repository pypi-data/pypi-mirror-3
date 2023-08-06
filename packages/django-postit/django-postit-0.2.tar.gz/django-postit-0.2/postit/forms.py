from django import forms
from django.contrib.auth.models import User
from django.forms import ModelForm

from postit.models import PostIt
from postit.choices import STATUS_CHOICES

class PostItForm(forms.ModelForm):
	class Meta:
		model = PostIt
		widget=forms.Select(choices=STATUS_CHOICES)