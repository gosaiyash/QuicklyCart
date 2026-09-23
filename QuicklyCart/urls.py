"""
URL configuration for QuicklyCart project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from QuicklyCart import view
from . import view
from QuicklyCart_app import views

urlpatterns = [
    path('superadmin/', admin.site.urls),
    path('', view.index),
    path('seller/', view.seller_page),
    path('delivery/', view.delivery_page),
    path('rider/rules/', view.rider_rules_page),
    path('product/', view.product_page),
    path('becomeSeller/', view.seller_home),
    path('becomeRider/', view.rider_home),
    path('admin/', view.admin_page),
    path('user_register_save/' , views.user_register, name='user_register_save'), 
    path('user_login/', views.user_login , name='user_login'),
    path('becomeSeller/user_login/', views.user_login , name='becomeSeller/user_login/'),
    path('product/user_login/', views.user_login , name='product/user_login'),
    path('logout/',views.logout_user , name='logout'),
    path('becomeSeller/logout/',views.logout_user , name='becomeSeller/logout'),
    path('verify_otp/',views.verify_otp , name='verify_otp'),
    path('resendotp/',views.resendotp , name='resendotp'),
    path('verify_seller_otp/',views.verify_seller_otp , name='verify_seller_otp'),
    path('becomeSeller/verify_seller_otp/',views.verify_seller_otp , name='becomeSeller/verify_seller_otp/'),
    path('rider/verify-otp/',views.verify_rider_otp , name='rider_verify_otp'),
    path('rider/resend-otp/',views.resend_rider_otp , name='rider_resend_otp'),
    path('becomeSeller/seller_register/' , views.seller_register, name='becomeSeller/seller_register/'),   
    path('becomeSeller/submit_seller_documents/' , views.seller_doc_save , name="becomeSeller/submit_seller_documents/"),
    path('seller/addproduct/' , views.addproduct , name='seller/addproduct/'),
    path('getproduct/' , views.get_product , name='getproduct/') ,
    path('reset_password_email/' , views.forgot_password ),
    path('reset_password_otp/' , views.verify_forgot_password_otp ),
    path('reset_password_newpassword/' , views.newpassword ),
    path('moreinforproduct/<product_id>/' , views.moreinforproduct  , name="moreinforproduct/"),
    path('delete/<int:product_id>/', views.DeleteProduct, name='DeleteProduct'),
    path("add_category/", views.add_category, name="add_category"),
    path("categories/add/<int:product_id>/", views.add_category, name="delete_category"),
    path("profile/" , views.profile , name="profile"),
    path('profile/update/', views.profile_update, name='profile_update'),
    path('orders', views.order_history, name='order_history'),
    path('update_product_form/<int:product_id>/', views.edit_product_view, name='update_product_form'),
    path('update_product_save/<int:product_id>/', views.update_product_save, name='update_product_save'),
    # User Management URLs for Admin Panel
    path('admin/delete-user/<int:user_id>/', views.delete_user, name='delete_user'),
    # Seller Management URLs for Admin Panel
    path('admin/approve-seller/<int:seller_id>/', views.approve_seller, name='approve_seller'),
    path('admin/reject-seller/<int:seller_id>/', views.reject_seller, name='reject_seller'),
    path('admin/approve-rider/<int:rider_id>/', views.approve_rider, name='approve_rider'),
    path('admin/reject-rider/<int:rider_id>/', views.reject_rider, name='reject_rider'),
    # Debug URL
    path('debug/categories/', views.debug_categories, name='debug_categories'),
    # Cart API
    path('cart/add/', views.cart_add, name='cart_add'),
    path('cart/update/', views.cart_update, name='cart_update'),
    path('cart/remove/', views.cart_remove, name='cart_remove'),
    # Buy Now Checkout
    path('buynow/<int:product_id>/', views.buynow_start, name='buynow_start'),
    path('checkout/address/', views.checkout_address, name='checkout_address'),
    path('checkout/payment/', views.checkout_payment, name='checkout_payment'),
    path('place-cod-order/', views.place_cod_order, name='place_cod_order'),
    path('place-cart-order/', views.place_cart_order, name='place_cart_order'),
    path('cart-checkout/', views.cart_checkout, name='cart_checkout'),
    # Seller order actions
    path('seller/order/status', views.seller_order_status_update, name='seller_order_status_update'),
    path('seller/order/status/', views.seller_order_status_update),
]
