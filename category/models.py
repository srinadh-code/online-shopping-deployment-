from django.db import models
from django.contrib.auth.models import User
from django.db import models
from django.utils import timezone
from datetime import timedelta
from django.contrib.auth.models import User
from django.db import models 
from django.db.models import Sum   

class ProductAttribute(models.Model):   # means which time it is like size,length or somthing
    name = models.CharField(max_length=50)
    def __str__(self):
        return self.name
    
class Category(models.Model):
    name=models.CharField(max_length=100)
    attributes = models.ManyToManyField(ProductAttribute, blank=True)
    def __str__(self):
        return self.name
    
class SubCategory(models.Model):
    category = models.ForeignKey(Category,on_delete=models.CASCADE, related_name="subcategories")
    name = models.CharField(max_length=100)
    image = models.ImageField(upload_to='subcategory_images/', blank=True, null=True)
    def __str__(self):
        return self.name

class Product(models.Model):
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    subcategory = models.ForeignKey(SubCategory, on_delete=models.CASCADE)
    name = models.CharField(max_length=200)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    image = models.ImageField(upload_to='products/')
    stock=models.IntegerField(default=0)
    low_stock_threshold = models.IntegerField(default=0)
    def __str__(self):
        return self.name
    def total_stock(self):
        return self.variants.aggregate(total=Sum('stock'))['total'] or 0

    #  AUTO SYNC (keeps old code working)
    def update_stock(self):
        self.stock = self.total_stock()
        self.save(update_fields=['stock'])

class Cart(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username}'s Cart"

class AttributeValue(models.Model):    # like M,L,XL,XXL
    attribute = models.ForeignKey(ProductAttribute, on_delete=models.CASCADE, related_name="values")
    value = models.CharField(max_length=50)
    def __str__(self):
        return f"{self.attribute.name} - {self.value}"
    
class ProductVariant(models.Model):  #adding M,L,XL   size to products
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="variants")
    attribute_value = models.ForeignKey(AttributeValue, on_delete=models.CASCADE)
    stock = models.IntegerField(default=10)

    def __str__(self):
        return f"{self.product.name} - {self.attribute_value.value}"
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        self.product.update_stock()

    def delete(self, *args, **kwargs):
        product = self.product
        super().delete(*args, **kwargs)
        product.update_stock()

    
class CartItem(models.Model):

    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name="items")

    product = models.ForeignKey(Product, on_delete=models.CASCADE)

    variant = models.ForeignKey(ProductVariant, on_delete=models.CASCADE)

    quantity = models.PositiveIntegerField(default=1)

    price = models.DecimalField(max_digits=10, decimal_places=2)
    def total_price(self):
        return self.product.price * self.quantity

    def __str__(self):
        return f"{self.product.name} ({self.quantity})"
    
class Order(models.Model):

    STATUS_CHOICES = (
        ('Placed', 'Placed'),
        ('Shipped', 'Shipped'),
        ('Delivered', 'Delivered'),
        ('Cancelled', 'Cancelled'),
    )

    PAYMENT_CHOICES = (
        ('COD', 'Cash On Delivery'),
        ('CARD', 'Card Payment'),
        ('UPI', 'UPI Payment'),
    )

    PAYMENT_STATUS = (
        ('Pending', 'Pending'),
        ('Paid', 'Paid'),
        ('Failed', 'Failed'),
    )

    user = models.ForeignKey(User, on_delete=models.CASCADE)

    total_amount = models.DecimalField(max_digits=10, decimal_places=2)

    discount_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='Placed'
    )

    payment_method = models.CharField(
        max_length=10,
        choices=PAYMENT_CHOICES,
        default='COD'
    )

    payment_status = models.CharField(
        max_length=10,
        choices=PAYMENT_STATUS,
        default='Pending'
    )

    created_at = models.DateTimeField(auto_now_add=True)

    estimated_delivery = models.DateTimeField(null=True, blank=True)

    delivered_at = models.DateTimeField(null=True, blank=True)
    stock_reduced = models.BooleanField(default=False)
    def __str__(self):
        return f"Order {self.id} - {self.status}"


class OrderItem(models.Model):

    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="items")

    product = models.ForeignKey(Product, on_delete=models.CASCADE)

    variant = models.ForeignKey(ProductVariant, on_delete=models.SET_NULL, null=True)

    quantity = models.IntegerField()

    price = models.DecimalField(max_digits=10, decimal_places=2)
class Wishlist(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)


class WishlistItem(models.Model):
    wishlist = models.ForeignKey(Wishlist, on_delete=models.CASCADE,  related_name="items")
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    added_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('wishlist', 'product')

class Review(models.Model):
    product = models.ForeignKey('Product', on_delete=models.CASCADE, related_name='reviews')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    rating = models.IntegerField()
    comment = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('product', 'user')

    def __str__(self):
        return f"{self.user} - {self.product} - {self.rating}"


class ReturnRequest(models.Model):
    STATUS_CHOICES = (
        ('Pending', 'Pending'),
        ('Approved', 'Approved'),
        ('Rejected', 'Rejected'),
    )

    REFUND_STATUS = (
        ('Not Initiated', 'Not Initiated'),
        ('Processing', 'Processing'),
        ('Completed', 'Completed'),
    )

    TYPE_CHOICES = (
        ('Return', 'Return'),
        ('Exchange', 'Exchange'),
    )

    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="returns")
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    request_type = models.CharField(max_length=10, choices=TYPE_CHOICES)
    reason = models.TextField()

    image = models.ImageField(upload_to='return_images/', null=True, blank=True)  

    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='Pending')
    refund_status = models.CharField(max_length=20, choices=REFUND_STATUS, default='Not Initiated')

    created_at = models.DateTimeField(auto_now_add=True) 

class Profile(models.Model):
    user=models.OneToOneField(User,on_delete=models.CASCADE)
    phone=models.CharField(max_length=10,blank=True) 
    address=models.TextField(max_length=50,blank=True)
    city=models.TextField(max_length=10,blank=True) 
    state=models.TextField(max_length=10,blank=True)
    pincode=models.TextField(max_length=6,blank=True)  
    profile_image=models.ImageField(upload_to="profile/",blank=True,null=True)


    def __str__(self):
        return self.user.username    
    


from django.db import models
from django.contrib.auth.models import User

class Address(models.Model):

    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)

    name = models.CharField(max_length=100)
    phone = models.CharField(max_length=10)   
    country_code = models.CharField(max_length=5, default="+91")

    house = models.CharField(max_length=200)
    area = models.CharField(max_length=200)

    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    pincode = models.CharField(max_length=6)

    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
 
 
class RecentlyViewed(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    product = models.ForeignKey('Product', on_delete=models.CASCADE)
    viewed_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('user', 'product')
        ordering = ['-viewed_at']

    def __str__(self):
        return f"{self.user} - {self.product}"