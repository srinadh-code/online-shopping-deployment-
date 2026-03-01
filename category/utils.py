from decimal import Decimal
from .models import Order

def apply_first_order_discount(user, total):
    has_order = False 
    if not has_order:
        discount = total * Decimal('0.30')   # ✅ FIXED
        final_total = total - discount
        return final_total, discount, True

    return total, Decimal('0.00'), False