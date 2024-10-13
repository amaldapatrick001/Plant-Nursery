from django import forms
from .models import Billing, Order

class BillingForm(forms.ModelForm):
    class Meta:
        model = Billing
        fields = [
            'first_name', 
            'last_name', 
            'district', 
            'street_address', 
            'town_city', 
            'postcode_zip', 
            'phone', 
            'email'
        ]

class OrderForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = [
            'user', 
            'billing', 
            'cart', 
            'payment_method', 
            'subtotal', 
            'total_discount', 
            'delivery_price', 
            'total_price'
        ]

    def clean(self):
        cleaned_data = super().clean()
        
        # Example validation: ensure total_price is not less than subtotal
        subtotal = cleaned_data.get('subtotal')
        total_discount = cleaned_data.get('total_discount')
        total_price = cleaned_data.get('total_price')

        if total_price < (subtotal - total_discount):
            raise forms.ValidationError("Total price cannot be less than the subtotal after discount.")

        return cleaned_data
