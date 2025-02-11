from django import forms
from django.contrib.auth.hashers import make_password
from .models import User_Reg, Login
from django.core.validators import RegexValidator
import re

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
from .models import Expert

class ExpertProfileUpdateForm(forms.ModelForm):
    EXPERTISE_CHOICES = [
        ('plant_diseases', 'Plant Diseases'),
        ('soil_fertility', 'Soil Fertility'),
        ('crop_management', 'Crop Management'),
        ('irrigation', 'Irrigation'),
        ('other', 'Other (Please Specify)'),  # Updated label
    ]

    QUALIFICATION_CHOICES = [
        ('bachelor_agriculture', 'Bachelor of Agriculture'),
        ('master_agriculture', 'Master of Agriculture'),
        ('agriculture_certification', 'Agriculture Certification'),
        ('horticulture_degree', 'Horticulture Degree'),
        ('crop_science_degree', 'Crop Science Degree'),
        ('soil_science_degree', 'Soil Science Degree'),
        ('plant_pathology_degree', 'Plant Pathology Degree'),
        ('agronomy_certification', 'Agronomy Certification'),
        ('irrigation_management_certification', 'Irrigation Management Certification'),
        ('pest_management_certification', 'Pest Management Certification'),
        ('diploma_agriculture', 'Diploma in Agriculture'),
        ('other', 'Other (Please Specify)'),  # Updated label
    ]

    availability_status = forms.ChoiceField(
        choices=[('available', 'Available'), ('unavailable', 'Unavailable')],
        widget=forms.RadioSelect(attrs={
            'class': 'form-check-input',
        }),
        initial='available'
    )

    expertise_area = forms.ChoiceField(
        choices=EXPERTISE_CHOICES, 
        required=True, 
        widget=forms.Select(attrs={
            'class': 'form-control',
            'id': 'expertise_area',
            'onchange': 'toggleOtherField(this, "other_expertise_area")'
        })
    )

    other_expertise_area = forms.CharField(
        max_length=255, 
        required=False, 
        widget=forms.TextInput(attrs={
            'class': 'form-control mt-2',
            'id': 'other_expertise_area',
            'placeholder': 'Please specify your expertise area',
            'style': 'display: none;'
        })
    )

    qualifications = forms.ChoiceField(
        choices=QUALIFICATION_CHOICES, 
        required=True, 
        widget=forms.Select(attrs={
            'class': 'form-control',
            'id': 'qualifications',
            'onchange': 'toggleOtherField(this, "other_qualification")'
        })
    )

    other_qualification = forms.CharField(
        max_length=255, 
        required=False, 
        widget=forms.TextInput(attrs={
            'class': 'form-control mt-2',
            'id': 'other_qualification',
            'placeholder': 'Please specify your qualification',
            'style': 'display: none;'
        })
    )

    availability_schedule = forms.CharField(
        required=False, 
        widget=forms.Textarea(attrs={
            'class': 'form-control', 
            'placeholder': 'Enter weekly availability (Sunday-Saturday) with times.'
        })
    )

    class Meta:
        model = Expert
        fields = [
            'expertise_area', 'qualifications', 'description',
            'profile_picture', 'specialization_tags', 'availability_status',
            'consultation_fee', 'certifications', 'contact_email',
            'contact_phone', 'location', 'languages', 'chat_enabled',
            'phone_enabled', 'meet_link', 'session_duration', 'session_price'
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Add any field customization here

from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth.models import User

class ExpertPasswordChangeForm(PasswordChangeForm):
    class Meta:
        model = User
        fields = ['old_password', 'new_password1', 'new_password2']




from django import forms

class DeliveryPersonnelRegistrationForm(forms.Form):
    # User_Reg fields
    first_name = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    last_name = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={'class': 'form-control'})
    )
    
    # DeliveryPersonnel fields
    area_of_delivery = forms.ChoiceField(
        choices=[
            ('', 'Select Delivery Area'),  # Add empty default choice
            ('kottayam', 'Kottayam'),
            ('pathanamthitta', 'Pathanamthitta'),
            ('idukki', 'Idukki'),
            ('thodupuzha', 'Thodupuzha'),
            ('ernakulam', 'Ernakulam'),
        ],
        widget=forms.Select(attrs={'class': 'form-control'}),
        required=True
    )
    
    status = forms.ChoiceField(
        choices=[
            ('available', 'Available'),
            ('busy', 'Busy'),
        ],
        initial='available',
        widget=forms.Select(attrs={'class': 'form-control'}),
        required=True
    )
    
    max_daily_orders = forms.IntegerField(
        initial=10,
        min_value=1,
        max_value=20,
        widget=forms.NumberInput(attrs={'class': 'form-control'})
    )
    
    latitude = forms.FloatField(required=True)
    longitude = forms.FloatField(required=True)

    def clean(self):
        cleaned_data = super().clean()
        latitude = cleaned_data.get('latitude')
        longitude = cleaned_data.get('longitude')
        
        if not latitude or not longitude:
            raise forms.ValidationError("Please select a location on the map")
        
        return cleaned_data

from django import forms
from .models import DeliveryPersonnel

class DeliveryPersonnelForm(forms.ModelForm):
    area_of_delivery = forms.ChoiceField(
        choices=[
            ('kottayam', 'Kottayam'),
            ('pathanamthitta', 'Pathanamthitta'),
            ('idukki', 'Idukki'),
            ('thodupuzha', 'Thodupuzha'),
            ('ernakulam', 'Ernakulam'),
        ],
        widget=forms.Select(attrs={
            'class': 'form-control',
            'placeholder': 'Select Delivery Area'
        })
    )
    
    status = forms.ChoiceField(
        choices=[('available', 'Available'), ('busy', 'Busy')],
        widget=forms.Select(attrs={
            'class': 'form-control',
            'placeholder': 'Select Status'
        })
    )

    class Meta:
        model = DeliveryPersonnel
        fields = ['area_of_delivery', 'status']
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['area_of_delivery'].label = "Delivery Area"
        self.fields['status'].label = "Availability Status"
        
        # Add any additional styling or attributes
        for field in self.fields:
            self.fields[field].widget.attrs.update({
                'class': 'form-control mb-3'
            })

class DeliveryProfileUpdateForm(forms.Form):
    first_name = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter First Name'
        })
    )
    
    last_name = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter Last Name'
        })
    )
    
    phone_number = forms.CharField(
        max_length=10,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter 10-digit phone number'
        })
    )
    
    vehicle_number = forms.CharField(
        max_length=15,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter vehicle number (e.g., KL01AB1234)'
        })
    )
    
    profile_picture = forms.ImageField(
        required=False,
        widget=forms.FileInput(attrs={
            'class': 'form-control',
            'accept': 'image/*'
        })
    )
    
    status = forms.ChoiceField(
        choices=[
            ('available', 'Available'),
            ('busy', 'Busy'),
        ],
        widget=forms.Select(attrs={
            'class': 'form-select'
        })
    )
