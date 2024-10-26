from django import forms
from .models import Billing

class CheckoutForm(forms.ModelForm):
    class Meta:
        model = Billing
        fields = ['first_name', 'last_name', 'district', 'street_address', 'town_city', 'postcode_zip', 'phone', 'email']
    
    first_name = forms.CharField(required=True, widget=forms.TextInput(attrs={'required': 'required'}))
    last_name = forms.CharField(required=True, widget=forms.TextInput(attrs={'required': 'required'}))
    district = forms.ChoiceField(choices=[('kottayam', 'Kottayam'), ('pathanamthitta', 'Pathanamthitta'),
                                          ('idukki', 'Idukki'), ('thodupuzha', 'Thodupuzha'),
                                          ('ernakulam', 'Ernakulam')], required=True)
    street_address = forms.CharField(required=True)
    town_city = forms.CharField(required=True)
    postcode_zip = forms.CharField(required=True)
    phone = forms.CharField(required=True)
    email = forms.EmailField(required=True)
