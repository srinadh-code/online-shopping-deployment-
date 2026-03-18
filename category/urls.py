from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboardview, name="dashboard"),
    
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
    path("cancel-order/<int:order_id>/", views.cancel_order, name="cancel_order"),
    path('invoice/<int:order_id>/', views.download_invoice, name='download_invoice'),
    path("profile/", views.profile, name="profile"),
    path("admin-login/", views.admin_login, name="admin_login"),
    path("admin-dashboard/", views.admin_dashboard, name="admin_dashboard"),
    path("admin-products/", views.admin_products, name="admin_products"),
    path("admin-orders/", views.admin_orders, name="admin_orders"),
    path("admin-customers/", views.admin_customers, name="admin_customers"),
    path("admin-order/<int:order_id>/", views.admin_order_detail, name="admin_order_detail"),
    path("admin-customer/<int:user_id>/", views.customer_orders, name="customer_orders"),
    path("edit-product/<int:id>/", views.edit_product, name="edit_product"),
    path("delete-product/<int:id>/", views.delete_product, name="delete_product"),
    path("cart/increase/<int:item_id>/",views.increase_quantity,name="increase_quantity"),
    path("cart/decrease/<int:item_id>/",views.decrease_quantity,name="decrease_quantity"),
    path("card-payment/", views.card_payment, name="card_payment"),
    path("upi-payment/", views.upi_payment, name="upi_payment"),
    path("payment-processing/", views.payment_processing, name="payment_processing"),
    path("create-order/", views.create_order, name="create_order"),
    path("order-success/", views.order_success, name="order_success"),
    path('find-similar/<int:product_id>/', views.find_similar, name="find_similar"),
    path("address/",views.address_page,name="address"),
    path("address/edit/<int:id>/", views.edit_address, name="edit_address"),
    path("address/delete/<int:id>/", views.delete_address, name="delete_address"),

    path("deliver/<int:id>/",views.deliver_here,name="deliver_here"),
]

