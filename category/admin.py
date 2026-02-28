from django.contrib import admin
from .models import Category,Product,SubCategory
from .models import Cart, CartItem
admin.site.register(Category)
admin.site.register(Product)
admin.site.register(SubCategory)
admin.site.register(Cart)
admin.site.register(CartItem)