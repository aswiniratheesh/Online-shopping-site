from django.urls import path
from . import views

urlpatterns=[
    path('add/<int:product_id>/',views.add_cart,name="add_cart"),
    path('cart_detail',views.cart,name="cart_detail"),    
    path('cart_remove', views.cart_remove, name="cart_remove"),
    path('full_remove/', views.full_remove, name="full_remove"),
    path('checkout/', views.checkout, name="checkout"),
    path('checkCoupon/', views.checkCoupon, name="checkCoupon"),
    path('add_item',views.add_item,name="add_item"),
    path('buy_now/<id>', views.buy_now, name='buy_now'),
    path('view_wishlist/<id>', views.view_wishlist, name='view_wishlist'),
    path('add_wishlist/<id>', views.add_wishlist, name='add_wishlist'),
    path('del_wishlist/<id>', views.del_wishlist, name='del_wishlist'),

]