from django.urls import path
from . import views

urlpatterns = [
    path("dashboard/", views.dashboardview, name="dashboard"),
    
    path("category/<int:category_id>/", views.category_view, name="category"),
    
    path("subcategory/<int:subcategory_id>/", views.subcategory_view, name="subcategory"),
    
    path("product/<int:product_id>/", views.product_detail, name="product_detail"),
    
    path("add-to-cart/<int:product_id>/", views.add_to_cart, name="add_to_cart"),
    
    path("buy-now/<int:product_id>/", views.buy_now, name="buy_now"),
    
    path("cart/", views.cart_view, name="cart"),
    
    path("remove-from-cart/<int:item_id>/", views.remove_from_cart, name="remove_from_cart"),
    
    path("place-order/", views.place_order, name="place_order"),
    
    path("my-orders/", views.my_orders, name="my_orders"),
    path("toggle-wishlist/<int:product_id>/", views.toggle_wishlist, name="toggle_wishlist"),
    path("wishlist/", views.wishlist_view, name="wishlist"),
    path("remove-from-wishlist/<int:item_id>/",
     views.remove_from_wishlist,
     name="remove_from_wishlist"),
    path("reset-orders/", views.reset_orders),
    path('return-request/<int:order_id>/', views.return_request, name='return_request'),
    path('my-returns/', views.my_returns, name='my_returns'),

]

