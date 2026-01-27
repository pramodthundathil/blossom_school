from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver
from .models import Income
from decimal import Decimal

@receiver(post_delete, sender=Income)
def delete_payment_on_income_delete(sender, instance, **kwargs):
    """
    When an Income item is deleted, delete the corresponding Payment
    if bill_number matches any payment_id.
    """
    from payments.models import Payment
    
    if instance.bill_number and instance.bill_number != "No Bill":
        # Using filter().delete() is safer than get() in case of duplicates or missing
        Payment.objects.filter(payment_id=instance.bill_number).delete()

@receiver(post_save, sender=Income)
def update_payment_on_income_update(sender, instance, **kwargs):
    """
    When an Income item is updated, update the corresponding Payment's total_amount.
    """
    from payments.models import Payment
    
    if instance.bill_number and instance.bill_number != "No Bill":
        payments = Payment.objects.filter(payment_id=instance.bill_number)
        for payment in payments:
            # Convert float to Decimal for currency
            try:
                # Use string conversion to avoid float precision issues
                new_amount = Decimal(str(instance.amount))
                
                # Update if different (comparing Decimal vs Decimal)
                if payment.total_amount != new_amount:
                    payment.total_amount = new_amount
                    payment.save()
                    
                    # Update first payment item to reflect the change
                    first_item = payment.payment_items.first()
                    if first_item:
                        # Calculate sum of other items
                        other_items_total = sum(item.amount for item in payment.payment_items.all() if item.id != first_item.id)
                        # New amount for first item = New Total - Other Items
                        first_item.amount = new_amount - other_items_total
                        first_item.save()

            except (ValueError, TypeError):
                pass
