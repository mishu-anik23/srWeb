from django.urls import path
from . import views
from . import cart_views

app_name = 'store'

urlpatterns = [
    # ... existing URLs ...
    path('', views.home, name='home'),
    path('products/', views.product_list, name='product_list'),
    path('category/<slug:slug>/', views.category_products, name='category_products'),
    path('product/<slug:slug>/', views.product_detail, name='product_detail'),

    # Cart URLs
    path('cart/', cart_views.cart_detail, name='cart_detail'),
    path('cart/add/<int:product_id>/', cart_views.cart_add, name='cart_add'),
    path('cart/remove/<int:product_id>/', cart_views.cart_remove, name='cart_remove'),
    path('cart/update/<int:product_id>/', cart_views.cart_update, name='cart_update'),
    path('cart/summary/', cart_views.cart_summary, name='cart_summary'),
]