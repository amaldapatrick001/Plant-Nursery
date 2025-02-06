from django import forms
from .models import QnASession
from userauths.models import Expert
from django.utils import timezone

class ScheduleMeetingForm(forms.ModelForm):
    max_participants = forms.IntegerField(
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': 'Maximum number of participants'
        })
    )
    
    start_date = forms.DateField(
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date'
        })
    )
    
    start_time = forms.TimeField(
        widget=forms.TimeInput(attrs={
            'class': 'form-control',
            'type': 'time'
        })
    )
    
    end_date = forms.DateField(
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date'
        })
    )
    
    end_time = forms.TimeField(
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
                'placeholder': 'Enter meeting title'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Describe the purpose of the consultation',
                'rows': 4
            }),
            'expert': forms.Select(attrs={
                'class': 'form-select'
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
            start_datetime = timezone.make_aware(
                timezone.datetime.combine(start_date, start_time)
            )
            end_datetime = timezone.make_aware(
                timezone.datetime.combine(end_date, end_time)
            )
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
            'max_participants': forms.NumberInput(attrs={'class': 'form-control'}),
        }
