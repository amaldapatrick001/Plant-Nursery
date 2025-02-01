from django import forms
from .models import QnASession
from userauths.models import Expert
from django.utils import timezone

class ScheduleMeetingForm(forms.ModelForm):
    max_participants = forms.IntegerField(
        min_value=1,
        max_value=50,
        initial=10,
        required=True,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': 'Maximum number of participants (1-50)'
        })
    )
    
    start_date = forms.DateField(
        required=True,
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date',
            'min': timezone.now().date().isoformat()
        })
    )
    
    start_time = forms.TimeField(
        required=True,
        widget=forms.TimeInput(attrs={
            'class': 'form-control',
            'type': 'time'
        })
    )
    
    end_date = forms.DateField(
        required=True,
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date',
            'min': timezone.now().date().isoformat()
        })
    )
    
    end_time = forms.TimeField(
        required=True,
        widget=forms.TimeInput(attrs={
            'class': 'form-control',
            'type': 'time'
        })
    )

    class Meta:
        model = QnASession
        fields = ['title', 'description', 'expert', 'max_participants']
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter meeting title',
                'required': True
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Describe the purpose of the consultation',
                'rows': 4,
                'required': True
            }),
            'expert': forms.Select(attrs={
                'class': 'form-select',
                'required': True
            })
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['expert'].queryset = Expert.objects.filter(availability_status='available')
        self.fields['expert'].empty_label = "Select an Expert"

    def clean(self):
        cleaned_data = super().clean()
        start_date = cleaned_data.get('start_date')
        start_time = cleaned_data.get('start_time')
        end_date = cleaned_data.get('end_date')
        end_time = cleaned_data.get('end_time')

        if all([start_date, start_time, end_date, end_time]):
            # Combine date and time
            start_datetime = timezone.make_aware(
                timezone.datetime.combine(start_date, start_time)
            )
            end_datetime = timezone.make_aware(
                timezone.datetime.combine(end_date, end_time)
            )

            # Store the combined datetime objects
            cleaned_data['start_time'] = start_datetime
            cleaned_data['end_time'] = end_datetime

        return cleaned_data

class ExpertScheduleMeetingForm(forms.ModelForm):
    class Meta:
        model = QnASession
        fields = ['title', 'description', 'max_participants', 'start_time', 'end_time']
        widgets = {
            'start_time': forms.DateTimeInput(attrs={'type': 'datetime-local', 'class': 'form-control'}),
            'end_time': forms.DateTimeInput(attrs={'type': 'datetime-local', 'class': 'form-control'}),
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'max_participants': forms.NumberInput(attrs={'class': 'form-control', 'min': 1, 'max': 50}),
        }

    def clean(self):
        cleaned_data = super().clean()
        start_time = cleaned_data.get('start_time')
        end_time = cleaned_data.get('end_time')
        
        if start_time and end_time:
            if start_time < timezone.now():
                raise forms.ValidationError("Start time cannot be in the past")
            
            if end_time <= start_time:
                raise forms.ValidationError("End time must be after start time")
            
            if (end_time - start_time).total_seconds() > 7200:  # 2 hours in seconds
                raise forms.ValidationError("Session duration cannot exceed 2 hours")
        
        return cleaned_data
