from django.urls import path
from . import views


urlpatterns = [
    path('', views.logincheck, name='logincheck'),
    path('logincheck', views.logincheck, name='logincheck'),
    path('signup', views.user_reg, name='signup'),
    path('user_login', views.user_login, name='user_login'),
    path('user_logout', views.user_logout, name='user_logout'),
    path('admin_logout', views.admin_logout, name='admin_logout'),
    path('phone_login', views.phone_login, name='phone_login'),
    path('login_otp', views.login_otp, name='login_otp'),
    path('reg_otp', views.reg_otp, name='reg_otp'),
    path('forgot_password', views.forgot_password, name='forgot_password'),
    path('forgot_otp', views.forgot_otp, name='forgot_otp'),
    path('reset_password', views.reset_password, name='reset_password'),

]
