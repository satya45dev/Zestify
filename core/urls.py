from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static
from django.views.static import serve
from django.urls import re_path

urlpatterns = [
    # General & Product Views
    path('', views.index, name='index'),
    path('product/<int:product_id>/', views.product_detail, name='product_detail'),
    path('category/<slug:slug>/', views.category_detail, name='category_detail'),
    path('search/', views.search_results, name='search_results'), 

    # Auth Views
    path('login/', views.login_view, name='login'),
    path('register/', views.register_view, name='user_register'),
    path('logout/', views.logout_view, name='logout'),
    
    # Dashboard & User Views
    path('dashboard/', views.user_dashboard, name='user_dashboard'),
    path('dashboard/settings/', views.account_settings_view, name='account_settings'),
    path('dashboard/orders/', views.track_orders_view, name='track_orders'),
    path('dashboard/wishlist/', views.wishlist_view, name='wishlist'),
    path('dashboard/wishlist/add/<int:product_id>/', views.add_to_wishlist, name='add_to_wishlist'),
    
    # Address Views
    path('addresses/', views.my_addresses_view, name='my_addresses'),
    path('addresses/add/', views.add_address_view, name='add_address'),
    # NOTE: You'll need to create views for edit/delete address actions
    # path('addresses/edit/<int:address_id>/', views.edit_address_view, name='edit_address'),
    # path('addresses/delete/<int:address_id>/', views.delete_address_view, name='delete_address'),
    # path('addresses/default/<int:address_id>/', views.set_default_address_view, name='set_default_address'),

    # Cart & Checkout Views
    path('cart/', views.cart_detail, name='cart_detail'),
    path('cart/add/<int:product_id>/', views.cart_add, name='cart_add'),
    path('cart/remove/<int:product_id>/', views.cart_remove, name='cart_remove'),
    path('checkout/', views.checkout_view, name='checkout'),
    path('payment-process/', views.process_payment, name='process_payment'),
    path('order-confirmation/<int:order_id>/', views.order_confirmation, name='order_confirmation'),

    # Payment Methods Views
    path('payments/', views.payment_methods_view, name='payment_methods'),
    path('payments/add/<str:method_type>/', views.add_payment_method_view, name='add_payment_method'), 
    path('payments/card/delete/<int:card_id>/', views.delete_card_view, name='delete_card'),
    path('payments/card/default/<int:card_id>/', views.set_default_card_view, name='set_default_card'),
    path('payments/upi/delete/<int:upi_id>/', views.delete_upi_view, name='delete_upi'),
    path('payments/upi/default/<int:upi_id>/', views.set_default_upi_view, name='set_default_upi'),
]

urlpatterns += [
    re_path(r'^media/(?P<path>.*)$', serve, {
        'document_root': settings.MEDIA_ROOT,
    }),
]