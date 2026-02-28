from django.contrib import admin
from .models import Category,Product,SubCategory
from .models import Cart, CartItem
from django.contrib import admin
from .models import (
    Category, Product, SubCategory,
    Cart, CartItem,
    Order, OrderItem,
    Wishlist, WishlistItem,
    ReturnRequest
)
admin.site.register(Category)
admin.site.register(SubCategory)
admin.site.register(Product)
admin.site.register(Cart)
admin.site.register(CartItem)
admin.site.register(Order)
admin.site.register(OrderItem)
admin.site.register(Wishlist)
admin.site.register(WishlistItem)



class ReturnRequestAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'order',
        'user',
        'request_type',
        'status',
        'refund_status',
        'created_at'
    )

    list_editable = ('status', 'refund_status')
    list_filter = ('status', 'request_type', 'refund_status')
    search_fields = ('user__username', 'order__id')

admin.site.register(ReturnRequest, ReturnRequestAdmin)
