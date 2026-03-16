from django.contrib import admin
from django import forms
from django.urls import path
from django.shortcuts import render

from .models import (
    Category, Product, SubCategory,
    Cart, CartItem,
    Order, OrderItem,
    Wishlist, WishlistItem,
    ReturnRequest,
    ProductAttribute,
    AttributeValue,
    ProductVariant
)

# ---------------- BASIC MODELS ----------------

admin.site.register(Category)
admin.site.register(SubCategory)
admin.site.register(Cart)
admin.site.register(CartItem)
admin.site.register(Order)
admin.site.register(OrderItem)
admin.site.register(Wishlist)
admin.site.register(WishlistItem)


# ---------------- RETURN REQUEST ADMIN ----------------

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


# ---------------- BULK ATTRIBUTE VALUE FORM ----------------

class AttributeValueForm(forms.Form):
    attribute = forms.ModelChoiceField(queryset=ProductAttribute.objects.all())
    values = forms.CharField(
        help_text="Enter multiple values separated by commas (Example: S,M,L,XL)"
    )


class AttributeValueAdmin(admin.ModelAdmin):

    def get_urls(self):
        urls = super().get_urls()

        custom_urls = [
            path(
                "bulk-add/",
                self.admin_site.admin_view(self.bulk_add_view),
                name="attributevalue-bulk-add"
            )
        ]

        return custom_urls + urls

    def bulk_add_view(self, request):

        if request.method == "POST":
            form = AttributeValueForm(request.POST)

            if form.is_valid():
                attribute = form.cleaned_data["attribute"]
                values = form.cleaned_data["values"].split(",")

                for value in values:
                    AttributeValue.objects.create(
                        attribute=attribute,
                        value=value.strip()
                    )

                self.message_user(request, "Values added successfully")

        else:
            form = AttributeValueForm()

        return render(request, "admin/bulk_attribute_values.html", {"form": form})


admin.site.register(ProductAttribute)
admin.site.register(AttributeValue, AttributeValueAdmin)


# ---------------- PRODUCT VARIANT INLINE ----------------

class ProductVariantInline(admin.TabularInline):
    model = ProductVariant
    extra = 5


class ProductAdmin(admin.ModelAdmin):
    inlines = [ProductVariantInline]


admin.site.register(ProductVariant)
admin.site.register(Product, ProductAdmin)