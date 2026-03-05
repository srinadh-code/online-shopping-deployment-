from django.db.models.signals import pre_save
from django.dispatch import receiver
from django.core.mail import send_mail
from django.conf import settings
from .models import Order

# @receiver(pre_save,sender=Order)
# def reduce_stock_on_deliveery(sender,instance,**kwargs):
#     if not instance.pk:
#         return
#     old_order=Order.objects.get(pk=instance.pk)

#     if old_order.status !='delivered' and instance.status == 'delivered':

#         for item in instance.items.all():
#             product=item.product
#             product.stock-=item.quantity
#             product.save()

#             if product.stock == 5 :
#                 send_mail(
#                     subject="LOw stock Alert",
#                     message=f"{product.name} stock reached 5",
#                     from_email=settings.DEFAULT_FROM_EMAIL,
#                     recipient_list=["ones12245@gmail.com"],
#                     fail_silently=False,
                # )





@receiver(pre_save, sender=Order)
def reduce_stock_on_first_delivery(sender, instance, **kwargs):

    if not instance.pk:
        return

    old_order = Order.objects.get(pk=instance.pk)

    # Trigger ONLY when status changes to Delivered first time
    if old_order.status != "Delivered" and instance.status == "Delivered":

        for item in instance.items.all():

            product = item.product

            # Prevent negative stock
            if product.stock >= item.quantity:
                product.stock -= item.quantity
                product.save()

                # Mail only when stock becomes 5
                if product.stock == 5:
                    send_mail(
                        subject="Low Stock Alert",
                        message=f"{product.name} stock reached 5",
                        from_email=settings.DEFAULT_FROM_EMAIL,
                        recipient_list=["ones12245@gmail.com"],
                        fail_silently=False,
                    )
from django.db.models.signals import pre_save
from django.dispatch import receiver
from .models import Order
from .service import reduce_stock


@receiver(pre_save, sender=Order)
def handle_stock_on_delivery(sender, instance, **kwargs):
    print("inside signal")
    # Skip new order creation
    if not instance.pk:
        return

    old_order = Order.objects.get(pk=instance.pk)

    # Reduce stock ONLY when:
    # 1. Status changes to Delivered
    # 2. Stock was NOT already reduced
    # print("OLD STATUS:", old_order.status)
    # print("NEW STATUS:", instance.status)
    # print("OLD stock_reduced:", old_order.stock_reduced)

    if (
        old_order.status != "Delivered"
        and instance.status == "Delivered"
        and not old_order.stock_reduced
    ):

        for item in instance.items.all():
            reduce_stock(item.product.id, item.quantity)

        # Mark as reduced
        instance.stock_reduced = True

# signals.py

from django.db.models.signals import post_save
from django.dispatch import receiver
from django.db import transaction
from .models import Order
from django.core.exceptions import ValidationError

@receiver(post_save, sender=Order)
def reduce_stock_on_delivery(sender, instance, created, **kwargs):

    # Do nothing when order is first created
    if created:
        return

    # Reduce stock only once when status becomes Delivered
    if instance.status == "Delivered" and not instance.stock_reduced:

        with transaction.atomic():

            for item in instance.items.select_related("product"):

                product = item.product

                if product.stock < item.quantity:
                    instance.status = "Processing"
                    instance.save(update_fields=["status"])
                    return

                product.stock -= item.quantity
                product.save()

        # Mark stock as reduced
        instance.stock_reduced = True
        instance.save(update_fields=["stock_reduced"])                    