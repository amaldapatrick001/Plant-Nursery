from django.db import models
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):#create table fields
    email = models.EmailField(unique=True, null=False)
    username = models.CharField(max_length=100)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']


    def __str__(self):
        return self.username
    