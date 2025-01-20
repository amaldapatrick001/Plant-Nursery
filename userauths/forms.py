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


class UpdateProfileForm(forms.ModelForm):
    class Meta:
        model = User_Reg
        fields = ['first_name', 'last_name', 'phoneno']


class UpdatePasswordForm(forms.Form):
    new_password = forms.CharField(
        widget=forms.PasswordInput,
        label="New Password",
        max_length=128,
        min_length=8,
        help_text="Password must be at least 8 characters long and include uppercase letters, lowercase letters, numbers, and special symbols."
    )
    confirm_password = forms.CharField(
        widget=forms.PasswordInput,
        label="Confirm Password",
        max_length=128,
        min_length=8
    )

    def clean(self):
        cleaned_data = super().clean()
        new_password = cleaned_data.get("new_password")
        confirm_password = cleaned_data.get("confirm_password")

        if new_password and confirm_password and new_password != confirm_password:
            raise forms.ValidationError("Passwords do not match.")

        return cleaned_data

from django import forms
from .models import User_Reg

class AddExpertForm(forms.Form):
    fname = forms.CharField(max_length=100, label="First Name")
    lname = forms.CharField(max_length=100, label="Last Name")
    email = forms.EmailField(label="Email Address")
    phone = forms.CharField(max_length=15, label="Phone Number")

from django import forms
from django import forms
from .models import Expert

class ExpertProfileUpdateForm(forms.ModelForm):
    EXPERTISE_CHOICES = [
        ('plant_diseases', 'Plant Diseases'),
        ('soil_fertility', 'Soil Fertility'),
        ('crop_management', 'Crop Management'),
        ('irrigation', 'Irrigation'),
        ('other', 'Other'),
    ]

    QUALIFICATION_CHOICES = [
        ('degree', 'Degree'),
        ('certification', 'Certification'),
        ('diploma', 'Diploma'),
        ('other', 'Other'),
    ]

    expertise_area = forms.ChoiceField(choices=EXPERTISE_CHOICES, required=True, widget=forms.Select(attrs={'class': 'form-control'}))
    other_expertise_area = forms.CharField(max_length=255, required=False, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Specify other expertise area'}))

    qualifications = forms.ChoiceField(choices=QUALIFICATION_CHOICES, required=True, widget=forms.Select(attrs={'class': 'form-control'}))
    other_qualification = forms.CharField(max_length=255, required=False, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Specify other qualification'}))

    class Meta:
        model = Expert
        fields = ['expertise_area', 'other_expertise_area', 'qualifications', 'other_qualification', 'description', 'profile_picture', 'specialization_tags', 'availability_schedule', 'availability_status', 'consultation_fee', 'certifications', 'contact_email', 'contact_phone', 'location', 'languages']


from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth.models import User

class ExpertPasswordChangeForm(PasswordChangeForm):
    class Meta:
        model = User
        fields = ['old_password', 'new_password1', 'new_password2']


