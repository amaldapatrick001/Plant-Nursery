from django import forms
from django.contrib.auth.forms import UserCreationForm
from userauths.models import User

class UserRegisterForm(UserCreationForm):
    username = forms.CharField(
        widget=forms.TextInput(attrs={
            "placeholder": "Username",
            "class": "form-control",
            "required": "required",
            "pattern": "[a-zA-Z0-9]{3,}",  # Example pattern
            "title": "Username must be at least 3 characters long and contain only letters and numbers.",
            "id": "username"
        })
    )
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={
            "placeholder": "Email",
            "class": "form-control",
            "required": "required",
            "id": "email"
        })
    )
    password1 = forms.CharField(
        widget=forms.PasswordInput(attrs={
            "placeholder": "Password",
            "class": "form-control",
            "required": "required",
            "pattern": "(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}",  # Pattern for strong password
            "title": "Password must be at least 8 characters long and include uppercase letters, lowercase letters, numbers, and symbols.",
            "id": "password1"
        })
    )
    password2 = forms.CharField(
        widget=forms.PasswordInput(attrs={
            "placeholder": "Confirm Password",
            "class": "form-control",
            "required": "required",
            "minlength": "8",
            "id": "password2"
        })
    )

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']
