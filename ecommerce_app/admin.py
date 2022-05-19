from django.contrib import admin
from . models import Category,Product
from cart.models import Coupons as Coupon,CouponCheck,Buynow,Wishlist
# Register your models here.
class CategoryAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ('name',)}
    list_display = ('name', 'slug')
admin.site.register(Category)


class ProductAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ('name',)}
    list_display = ('name', 'slug')
admin.site.register(Product)

admin.site.register(CouponCheck)
admin.site.register(Coupon)
admin.site.register(Buynow)
admin.site.register(Wishlist)
