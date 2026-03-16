from django.db import transaction
from django.core.mail import send_mail
from django.conf import settings
from .models import Product
def reduce_stock(product_id, quantity):

    with transaction.atomic():

        product = Product.objects.select_for_update().get(pk=product_id)

        if product.stock < quantity:
            return False

        old_stock = product.stock
        product.stock -= quantity

        if (
            old_stock > product.low_stock_threshold
            and product.stock <= product.low_stock_threshold
            and not product.low_stock_alert_sent
        ):
            send_mail(
                f"Low Stock Alert - {product.name}",
                f"Current stock: {product.stock}",
                settings.DEFAULT_FROM_EMAIL,
                ["admin@example.com"],
            )

            product.low_stock_alert_sent = True

        product.save()

        return True