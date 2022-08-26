from turtle import title
from django.db import models
from django.contrib.auth.models import User

# Create your models here.


class Issue(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=100)
    content = models.TextField(max_length=2500)

    def __str__(self):
        return self.title
