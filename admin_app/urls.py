from django.urls import path
from . import views


urlpatterns = [
    path('admin_home', views.admin_home, name='admin_home'),

# category
    path('category', views.category, name="category"),
    path('add_category/', views.add_category, name="add_category"),
    path('add_cat', views.add_cat, name="add_cat"),
    path('admin_category_update/<slug>', views.admin_category_update, name='admin_category_update'),
    path('delete/', views.delete, name="delete"),
    # path('delete_cat/<id>', views.delete_cat, name="delete_cat"),

# products
    path('product_man', views.product_man, name='product_man'),
    path('add_product/', views.add_product, name='add_product'),
    path('product_update/<slug>/', views.product_update, name='product_update'),
    path('delete_pro/', views.delete_pro, name="delete_pro"),
    # path('delete_product/<id>', views.delete_product, name="delete_product"),

# user
    path('user_man', views.user_man, name='user_man'),
    path('unblock_user/', views.unblock_user, name='unblock_user'),
    path('block_user/', views.block_user, name='block_user'),

#order
    path('active_order', views.active_order, name='active_order'),
    path('ad_order_history', views.ad_order_history, name='ad_order_history'),

#coupon
    path('admin_coupon/', views.admin_coupon, name='admin_coupon'),
    path('admin_coupon_list/', views.admin_coupon_list, name='admin_coupon_list'),
    path('coupon_edit/<int:id>/', views.coupon_edit, name='coupon_edit'),
    path('coupon_delete/', views.coupon_delete, name='coupon_delete'),

#report
    path('order_reports/', views.order_reports, name='order_reports'),
    path('order_export_csv/', views.order_export_csv, name='order_export_csv'),
    path('order_export_excel/', views.order_export_excel, name='order_export_excel'),
    path('order_export_pdf/', views.order_export_pdf, name='order_export_pdf'),
]