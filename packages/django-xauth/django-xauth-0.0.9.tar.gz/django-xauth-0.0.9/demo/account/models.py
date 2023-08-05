from django.db import models

class Profile(models.Model):
    user = models.ForeignKey('auth.User')
    country = models.CharField(max_length=255)
    name = models.CharField(max_length=255)
