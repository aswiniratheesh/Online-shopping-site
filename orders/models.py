from django.db import models
from accounts.models import Account
from ecommerce_app.models import Product
from cart.models import Coupons as Coupon

# Create your models here.


class Payment(models.Model):
    user = models.ForeignKey(Account, on_delete=models.CASCADE)
    payment_id = models.CharField(max_length=100)
    payment_method = models.CharField(max_length=100)
    amount_paid = models.CharField(max_length=100)   #total amount paid
    status = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)

    def _str_(self):
        return self.payment_id



class Order(models.Model):
    STATUS = (
        ('New', 'New'),
        ('Accepted','Accepted'),
        ('Completed', 'Completed'),
        ('Cancelled', 'Cancelled'),
        ('Delivered', 'Delivered'),
        ('Returned', 'Returned'),
    )

    user = models.ForeignKey(Account, on_delete=models.SET_NULL, null=True)
    payment = models.ForeignKey(Payment, on_delete=models.SET_NULL, null=True, blank=True)
    order_number = models.CharField(max_length=20)
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    phone = models.CharField(max_length=15)
    email = models.EmailField(max_length=50)
    address_line_1 = models.CharField(max_length=50)
    address_line_2 = models.CharField(max_length=50, blank=True)
    country = models.CharField(max_length=50)
    state = models.CharField(max_length=50)
    city = models.CharField(max_length=50)
    pincode = models.CharField(max_length=10)
    order_total = models.FloatField()
    status = models.CharField(max_length=10, choices=STATUS, default='Placed')
    ip = models.CharField(blank=True, max_length=20)
    is_ordered = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now_add=True)
    coupon = models.ForeignKey(Coupon, null=True, on_delete=models.CASCADE)
    def full_name(self):
        return f'{self.first_name} {self.last_name}'

    def full_address(self):
        return f'{self.address_line_1} {self.address_line_2}'

    def _str_(self):
        return self.full_name()


class OrderProduct(models.Model):
    STATUS = (
        ('New', 'New'),
        ('Accepted','Accepted'),
        ('Completed', 'Completed'),
        ('Cancelled', 'Cancelled'),
        ('Delivered', 'Delivered'),
        ('Returned', 'Returned'),
    )
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    payment = models.ForeignKey(Payment, on_delete=models.SET_NULL, blank=True, null=True)
    user = models.ForeignKey(Account, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.IntegerField()
    product_price = models.FloatField()
    ordered = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=10, choices=STATUS, default='Placed')

    def _str_(self):
        return self.product.name
    


class DeliveryAddress(models.Model):
    user           = models.ForeignKey(Account,on_delete=models.CASCADE)
    first_name     = models.CharField(max_length=50)
    last_name      = models.CharField(max_length=50)
    phone          = models.CharField(max_length=15)
    email          = models.EmailField()
    country        = models.CharField(max_length=30)
    state          = models.CharField(max_length=30)
    city           = models.CharField(max_length=50)
    pincode        = models.CharField(max_length=10)
    address_line_1 = models.CharField(max_length=50)
    address_line_2 = models.CharField(max_length=50)

    def __str__(self):
        return self.first_name
