from django.db import models
<<<<<<< HEAD
from django.utils import timezone

class UserType(models.Model):
    utid = models.AutoField(primary_key=True)
    usertype = models.CharField(max_length=50)

    def __str__(self):
        return self.usertype

class User_Reg(models.Model):
    uid = models.AutoField(primary_key=True)
    user_type = models.ForeignKey(UserType, on_delete=models.SET_NULL, null=True)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    phoneno = models.CharField(max_length=15)
    date_time_reg = models.DateTimeField(auto_now_add=True)
    status = models.BooleanField(default=True)  # Automatically set status to True upon registration

    def __str__(self):
        return f'{self.first_name} {self.last_name}'

class Login(models.Model):
    login_id = models.AutoField(primary_key=True)
    uid = models.ForeignKey(User_Reg, on_delete=models.CASCADE)
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=128)
    status = models.BooleanField(default=True)  # Status set to True at the time of registration (auto-login)
    last_login = models.DateTimeField(null=True, blank=True)
    last_logout = models.DateTimeField(null=True, blank=True)
    login_count = models.IntegerField(default=0)

    def get_email_field_name(self):
        return 'email'

    def login(self):
        """ Logs the user in by updating the login timestamp, status, and login count. """
        self.status = True  # Set status to True on login
=======
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.utils import timezone


# UserType Model
class UserType(models.Model):
    user_type_id = models.AutoField(primary_key=True)
    user_type_name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.user_type_name


class CustomUserManager(BaseUserManager):
    def create_user(self, email, first_name, last_name, phoneno, password=None, **extra_fields):
        if not email:
            raise ValueError('The Email field must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, username=email, first_name=first_name, last_name=last_name, phoneno=phoneno, **extra_fields)  # Set username=email
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if password is None:
            raise TypeError('Superusers must have a password.')

        return self.create_user(email=email, username=email, first_name='', last_name='', phoneno='', password=password, **extra_fields)  # Set username=email


class User(AbstractUser):
    phoneno = models.CharField(max_length=15, unique=True)
    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=30)
    email = models.EmailField(unique=True, null=False)
    user_type = models.ForeignKey(UserType, on_delete=models.SET_NULL, null=True)

    username = models.CharField(max_length=150, unique=True, null=True, blank=True)  # Add this line to avoid `username` issues
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name', 'phoneno']

    objects = CustomUserManager()

    def __str__(self):
        return self.email


class Login(models.Model):
    login_id = models.AutoField(primary_key=True)
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    status = models.CharField(max_length=20, choices=[('active', 'Active'), ('deleted', 'Deleted'), ('logged_in', 'Logged In'), ('logged_out', 'Logged Out')])
    last_login = models.DateTimeField(null=True, blank=True)
    login_count = models.IntegerField(default=0)

    def __str__(self):
        return f'{self.user.email} - {self.status}'

    def login(self):
        self.status = 'logged_in'
>>>>>>> origin/main
        self.last_login = timezone.now()
        self.login_count += 1
        self.save()

    def logout(self):
<<<<<<< HEAD
        """ Logs the user out by updating the logout timestamp and status. """
        self.status = False  # Set status to False on logout
        self.last_logout = timezone.now()
        self.save()

    def __str__(self):
        return f'Login entry for {self.email}'
=======
        self.status = 'logged_out'
        self.save()
>>>>>>> origin/main
