from celery import shared_task
from django.utils.timezone import now
from datetime import timedelta
from .models import Batch

@shared_task
def update_batch_prices():
    batches = Batch.objects.filter(stock_quantity__gt=0)
    for batch in batches:
        if batch.updated_on + timedelta(days=30) <= now():
            batch.price += 10
            batch.updated_on = now()
            batch.save()
