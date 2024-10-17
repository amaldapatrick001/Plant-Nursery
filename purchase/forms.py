from django import forms
from .models import Billing

from django import forms

class CheckoutForm(forms.Form):
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
