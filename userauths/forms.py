from django import forms
from django.contrib.auth.hashers import make_password
from .models import User_Reg, Login

class RegistrationForm(forms.ModelForm):

    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'Email Address'
        })
    )
    phoneno = forms.CharField(
        max_length=15,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Phone Number'
        }),
    ) 

    password1 = forms.CharField(
        label='Password',
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Password',
            'pattern': r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&#])[A-Za-z\d@$!%*?&#]{8,}$',
            'title': 'Password must be at least 8 characters long and include uppercase letters, lowercase letters, numbers, and symbols.'
        })
    )

    password2 = forms.CharField(
        label='Confirm Password',
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Confirm Password'
        })
    )

    class Meta:
        model = User_Reg
        fields = ['first_name', 'last_name', 'phoneno', 'email']

    def clean(self):
        cleaned_data = super().clean()
        password1 = cleaned_data.get("password1")
        password2 = cleaned_data.get("password2")

        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("Passwords do not match.")

        return cleaned_data

    def save(self, commit=True):
        user = super().save(commit=False)
        if commit:
            user.save()
            # Create the login instance with hashed password
            Login.objects.create(
                uid=user,
                email=self.cleaned_data['email'],
                password=make_password(self.cleaned_data['password1']),
                login_count=0,
                status=False
            )
        return user


    
class LoginForm(forms.ModelForm):
    class Meta:
        model = Login
        fields = ['email', 'password']
        widgets = {
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'Email Address'
            }),
            'password': forms.PasswordInput(attrs={
                'class': 'form-control',
                'placeholder': 'Password'
            }),
        }



from django import forms
from django.contrib.auth.forms import PasswordResetForm, SetPasswordForm
from .models import Login

class CustomPasswordResetForm(forms.Form):
    email = forms.EmailField(
        label="Email",
        max_length=254,
        widget=forms.EmailInput(attrs={'autocomplete': 'email', 'class': 'form-control'})
    )

    def clean_email(self):
        email = self.cleaned_data['email']
        if not Login.objects.filter(email=email).exists():
            raise forms.ValidationError("No user is associated with this email address.")
        return email

class CustomSetPasswordForm(SetPasswordForm):
    new_password1 = forms.CharField(
        label="New password",
        widget=forms.PasswordInput(attrs={
            'autocomplete': 'new-password',
            'class': 'form-control',
            'placeholder': 'Enter new password',
            'pattern': r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&#])[A-Za-z\d@$!%*?&#]{8,}$',
            'title': 'Password must be at least 8 characters long and include uppercase letters, lowercase letters, numbers, and symbols.'
        })
    )
    
    new_password2 = forms.CharField(
        label="Confirm new password",
        widget=forms.PasswordInput(attrs={
            'autocomplete': 'new-password',
            'class': 'form-control',
            'placeholder': 'Confirm new password',
        })
    )
    
    def clean_new_password2(self):
        password1 = self.cleaned_data.get('new_password1')
        password2 = self.cleaned_data.get('new_password2')
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("Passwords do not match.")
        return password2
