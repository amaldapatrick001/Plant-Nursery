from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager

# UserType Model
class UserType(models.Model):
    user_type_id = models.AutoField(primary_key=True)
    user_type_name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.user_type_name

# Custom User Manager
class CustomUserManager(BaseUserManager):
    def create_user(self, email, first_name, last_name, phoneno, password=None, **extra_fields):
        if not email:
            raise ValueError('The Email field must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, first_name=first_name, last_name=last_name, phoneno=phoneno, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        # Create a corresponding Login entry
        Login.objects.create(user=user, password=user.password, status='active')
        return user

    def create_superuser(self, email, first_name, last_name, phoneno, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(email, first_name, last_name, phoneno, password, **extra_fields)

# Custom User Model
class User(AbstractUser):
    user_id = models.AutoField(primary_key=True)
    phoneno = models.CharField(max_length=15, unique=True)
    email = models.EmailField(unique=True, null=False)
    user_type = models.ForeignKey(UserType, on_delete=models.SET_NULL, null=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name', 'phoneno']

    objects = CustomUserManager()

    def __str__(self):
        return self.email

# Login Model
class Login(models.Model):
    login_id = models.AutoField(primary_key=True)
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    password = models.CharField(max_length=255)
    status = models.CharField(max_length=20, choices=[('active', 'Active'), ('deleted', 'Deleted')])
    last_login = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f'{self.user.email} - {self.status}'
