from django.db import transaction
from django.core.mail import send_mail
from django.conf import settings
from .models import Product


def reduce_stock(product_id, quantity):

    with transaction.atomic():

        product = Product.objects.select_for_update().get(pk=product_id)

        if product.stock < quantity:
            raise ValueError("Insufficient stock")

        # IMPORTANT — capture old stock BEFORE deduction
        old_stock = product.stock

        product.stock -= quantity

        print("OLD:", old_stock)
        print("NEW:", product.stock)
        print("THRESHOLD:", product.low_stock_threshold)

        # Low stock condition
        if (
            old_stock > product.low_stock_threshold
            and product.stock <= product.low_stock_threshold
            and not product.low_stock_alert_sent
        ):
            print("EMAIL CONDITION PASSED")

            send_mail(
                f"Low Stock Alert - {product.name}",
                f"Current stock: {product.stock}",
                settings.DEFAULT_FROM_EMAIL,
                ["admin@example.com"],
                fail_silently=False,
            )

            product.low_stock_alert_sent = True

        product.save()