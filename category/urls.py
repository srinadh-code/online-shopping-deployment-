# from django.urls import path
# from .views import dashboardview
# urlpatterns = [
#     path("dashboard/",dashboardview,name="dashboard"),
# ]
from django.urls import path
from . import views

urlpatterns = [
    path("dashboard/", views.dashboardview, name="dashboard"),
    path('category/<int:id>/', views.category_view, name='category'),
    path('subcategory/<int:id>/', views.subcategory_view, name='subcategory'),
]