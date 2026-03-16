from decimal import Decimal
from .models import Order

def apply_first_order_discount(user, total):

    has_order = Order.objects.filter(user=user).exists()

    if not has_order:
        discount = total * Decimal('0.30')
        final_total = total - discount
        return final_total, discount, True

    return total, Decimal('0.00'), False


import random
from datetime import timedelta
from django.utils import timezone

def predict_delivery():

    days = random.randint(1,7)

    delivery_date = timezone.now() + timedelta(days=days)

    return delivery_date


from decimal import Decimal
from .models import Order

def apply_first_order_discount(user, total):

    has_order = Order.objects.filter(user=user).exists()

    if not has_order:
        discount = total * Decimal('0.30')
        final_total = total - discount
        return final_total, discount, True

    return total, Decimal('0.00'), False


import random
from datetime import timedelta
from django.utils import timezone

def predict_delivery():

    days = random.randint(1,7)

    delivery_date = timezone.now() + timedelta(days=days)

    return delivery_date

