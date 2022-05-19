from django.db import models
from ecommerce_app.models import Product
from accounts.models import Account

class Cart(models.Model):
    cart_id=models.CharField(max_length=250, blank=True)
    date_added=models.DateField(auto_now_add=True)
    class Meta:
        db_table='Cart'
        ordering=['date_added']
    def __str__(self):
        return self.cart_id


class CartItem(models.Model):
    user = models.ForeignKey(Account,on_delete=models.CASCADE , null=True)
    product=models.ForeignKey(Product,on_delete=models.CASCADE)
    cart=models.ForeignKey(Cart, on_delete=models.CASCADE, null=True)
    quantity=models.IntegerField()
    active=models.BooleanField(default=True)

    class Meta:
        db_table = 'CartItem'
    def sub_total(self):
        return self.product.price*self.quantity
    def __str__(self):
        return self.product



class Coupons(models.Model):
    code = models.CharField(max_length=20)
    discount = models.CharField(max_length=3)
    status = models.BooleanField(default=True)
    valid_from = models.DateField()
    valid_to = models.DateField()

    def __str__(self):
        return self.code

class CouponCheck(models.Model):
    coupon = models.ForeignKey(Coupons, on_delete=models.CASCADE)
    user = models.ForeignKey(Account, on_delete=models.CASCADE)


class Buynow(models.Model):
    user = models.ForeignKey(Account, on_delete=models.CASCADE, null=True)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, null=True)
    quantity = models.IntegerField()
    is_active = models.BooleanField(default=True)

    def sub_total(self):
        return self.product.price * self.quantity

    def __str__(self):
        return str(self.product)

class Wishlist(models.Model):
    user = models.ForeignKey(Account,on_delete=models.CASCADE)
    product = models.ForeignKey(Product,on_delete=models.CASCADE)
    active = models.BooleanField(default=False)
