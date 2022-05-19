from django import forms
from django.db import models
from django.db.models import fields
from orders.models import Order
from django import forms
from accounts.models import Account
from .models import DeliveryAddress


class OrderForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ['first_name', 'last_name', 'phone', 'email','address_line_1','address_line_2','country','state','city','pincode']


class DeliveryAddressForm(forms.ModelForm):
    class Meta:
        model = DeliveryAddress
        fields= ['first_name', 'last_name', 'phone', 'email','address_line_1','address_line_2','country','state','city','pincode']

    def init(self, *args, **kwargs):
        super(DeliveryAddressForm, self).init(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs['class'] = 'form-control'