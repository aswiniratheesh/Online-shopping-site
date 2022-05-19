from orders.models import DeliveryAddress, Order
from django.contrib import admin
from orders.models import OrderProduct,Order, Payment
# Register your models here.


admin.site.register(Order)

admin.site.register(OrderProduct)

admin.site.register(Payment)

admin.site.register(DeliveryAddress)
