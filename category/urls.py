
# from django.urls import path
# from . import views

# urlpatterns = [
#     path("dashboard/", views.dashboardview, name="dashboard"),
#     path('category/<int:id>/', views.category_view, name='category'),
#     path("subcategory/<int:subcategory_id>/", views.subcategory_view, name="subcategory"),
#     path("product/<int:product_id>/", views.product_detail, name="product_detail"),
# ]

from django.urls import path
from . import views

urlpatterns = [
    path("dashboard/", views.dashboardview, name="dashboard"),
    path("category/<int:category_id>/", views.category_view, name="category"),
    path("subcategory/<int:subcategory_id>/", views.subcategory_view, name="subcategory"),
    path("product/<int:product_id>/", views.product_detail, name="product_detail"),
]