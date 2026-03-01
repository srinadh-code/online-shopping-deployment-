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