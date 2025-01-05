from django.core.management.base import BaseCommand
from datetime import date, timedelta
from payment.models import Payment

class Command(BaseCommand):
    help = "Перевіряє майбутні платежі"

    def handle(self, *args, **kwargs):
        today = date.today()
        upcoming_payments = Payment.objects.filter(
            next_payment_date__lte=today + timedelta(days=7),
            next_payment_date__gte=today
        )

        for payment in upcoming_payments:
            self.stdout.write(f"Наближається дата платежу для {payment.service.name}")
