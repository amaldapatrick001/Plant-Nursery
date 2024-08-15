from django.contrib import admin
from .models import UserType, User, Login

admin.site.register(UserType)
admin.site.register(User)
admin.site.register(Login)
