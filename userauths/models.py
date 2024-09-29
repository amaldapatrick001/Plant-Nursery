from django.db import models
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

from django.contrib.auth.hashers import make_password, check_password

class Login(models.Model):
    login_id = models.AutoField(primary_key=True)
    uid = models.ForeignKey(User_Reg, on_delete=models.CASCADE)
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=128)  # Store hashed password
    status = models.BooleanField(default=True)
    last_login = models.DateTimeField(null=True, blank=True)
    last_logout = models.DateTimeField(null=True, blank=True)
    login_count = models.IntegerField(default=0)

    def get_email_field_name(self):
        return 'email'
    
    def set_password(self, raw_password):
        """ Hashes the password before storing it """
        self.password = make_password(raw_password)
        self.save()

    def check_password(self, raw_password):
        """ Checks if the provided password matches the stored hash """
        return check_password(raw_password, self.password)
    
    def login(self):
        """ Logs the user in by updating the login timestamp, status, and login count. """
        self.status = True  # Set status to True on login
        self.last_login = timezone.now()
        self.login_count += 1
        self.save()

    def logout(self):
        """ Logs the user out by updating the logout timestamp and status. """
        self.status = False  # Set status to False on logout
        self.last_logout = timezone.now()
        self.save()

    def __str__(self):
        return f'Login entry for {self.email}'
