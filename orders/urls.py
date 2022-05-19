from django.urls import path
from . import views

urlpatterns = [
    path('place_order/', views.place_order, name='place_order'),
    path('payment/', views.payment, name='payment'),
    path('order_complete/', views.order_complete, name='order_complete'),
    path('order_history/', views.order_history, name='order_history'),
    path('status/', views.status, name='status'),
    path('order_cancel/<orderPro_id>', views.order_cancel, name='order_cancel'),
    path('order_return/<orderPro_id>', views.order_return, name='order_return'),
    path('add_address/', views.add_address, name='add_address'),
    path('buynow_place_order', views.buynow_place_order, name='buynow_place_order'),
    path('buynow_payment', views.buynow_payment, name='buynow_payment'),

]