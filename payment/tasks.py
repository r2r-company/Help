from celery import shared_task
from datetime import date, timedelta
from payment.models import Payment

@shared_task
def check_payment_reminders():
    today = date.today()
    upcoming_payments = Payment.objects.filter(
        next_payment_date__lte=today + timedelta(days=7),
        next_payment_date__gte=today
    )

    for payment in upcoming_payments:
        # Виконуйте логіку сповіщення, наприклад, надсилайте email.
        print(f"Наближається дата платежу для {payment.service.name}")
