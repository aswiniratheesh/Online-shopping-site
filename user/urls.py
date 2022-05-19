from django.urls import path
from . import views

urlpatterns = [
    path('', views.product_man, name='product_man')
]
