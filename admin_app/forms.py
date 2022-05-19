from admin_app import models
from accounts.models import Account
from ecommerce_app.models import Category, Product
from django import forms
from django.db.models import fields
from orders.models import Order
from cart.models import CouponCheck,Coupons as Coupon

#category
class CategoryForm(forms.ModelForm):
    image1 = forms.ImageField(required=False, error_messages={'invalid':("Image file only")}, widget=forms.FileInput)
    def __init__(self, *args, **kwargs):
        super(CategoryForm, self).__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs['class'] = 'form-control'

    class Meta:
        model=Category
        fields = ('image1','name','slug','desc')

    def save(self):
        photo = super(CategoryForm, self).save()
        return photo

#product
class ProductForm(forms.ModelForm):
    image1 = forms.ImageField(required=False, error_messages={'invalid':("Image file only")}, widget=forms.FileInput)
    image2 = forms.ImageField(required=False, error_messages={'invalid':("Image file only")}, widget=forms.FileInput)
    image3 = forms.ImageField(required=False, error_messages={'invalid':("Image file only")}, widget=forms.FileInput)
    image4 = forms.ImageField(required=False, error_messages={'invalid':("Image file only")}, widget=forms.FileInput)

    class Meta:
        model=Product
        fields = ('image1','image2','image3','image4','name','slug','price','offer','desc','category','stock')


    def save(self):
        photo = super(ProductForm, self).save()
        return photo


# user address
class AddressForm(forms.ModelForm):
    class Meta:
        model=Account
        fields=['country','state','town','pin','district','address']


#user profile
class UserForm(forms.ModelForm):
    image = forms.ImageField(required=False, error_messages={'invalid':("Image file only")}, widget=forms.FileInput)

    class Meta:
        model=Account
        fields=['first_name','last_name','phone_no','email','image']

    def save(self):
        photo = super(UserForm, self).save()
        return photo


#checkout
class CheckoutForm(forms.ModelForm):
    class Meta:
        model=Account
        fields=['first_name','last_name','phone_no','email','address','town','pin','district','state','country']

#order
class OrderForm(forms.ModelForm):
    class Meta:
        model=Order
        fields='__all__'

    def __init__(self, *args, **kwargs):
        super(OrderForm, self).__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs['class'] = 'form-control'
#date

class DateInput(forms.DateInput):
    input_type = 'date'

#coupon
class CouponForm(forms.ModelForm):
    class Meta:
        model = Coupon
        fields = ['code', 'discount','valid_from','valid_to']
        widgets = {
            'valid_from': DateInput(),
            'valid_to': DateInput()

        }
class CatofferForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['cat_offer']