from django.db import models
from django.contrib.auth.models import User

from choices import COLOR_CHOICES, STATUS_CHOICES
from colors.fields import ColorField

class UserProfile(models.Model):
	user = models.OneToOneField(User)
	color = ColorField()
	
class PostIt(models.Model):
    title = models.CharField(max_length=20)
    description = models.CharField(max_length=100)
    user_to = models.ForeignKey(User, related_name='user_to')
    user_from = models.ForeignKey(User, related_name='user_from')
    status = models.CharField(max_length=6,choices=STATUS_CHOICES)