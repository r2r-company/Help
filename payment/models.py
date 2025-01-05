from django.db import models

class PaymentService(models.Model):
    name = models.CharField(max_length=255, verbose_name="Назва")
    link = models.URLField(verbose_name="Посилання")
    login = models.CharField(max_length=255, verbose_name="Логін")
    password = models.CharField(max_length=255, verbose_name="Пароль")

    def __str__(self):
        return self.name


class Payment(models.Model):
    service = models.ForeignKey(PaymentService, on_delete=models.CASCADE, verbose_name="Сервіс")
    current_payment_date = models.DateField(verbose_name="Дата поточного платежу")
    next_payment_date = models.DateField(verbose_name="Дата наступного платежу")
    amount = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Сума платежу")
    reminder_days = models.IntegerField(default=7, verbose_name="Дні до нагадування")

    CURRENCY_CHOICES = [
        ('UAH', 'Гривня'),
        ('EUR', 'Євро'),
        ('USD', 'Долар США'),
    ]
    CURRENCY_SYMBOLS = {
        'UAH': '₴',
        'EUR': '€',
        'USD': '$',
    }
    currency = models.CharField(
        max_length=3,
        choices=CURRENCY_CHOICES,
        default='UAH',
        verbose_name="Валюта"
    )

    def __str__(self):
        return f"{self.service.name} - {self.amount} {self.get_currency_display()}"

    def get_formatted_amount(self):
        symbol = self.CURRENCY_SYMBOLS.get(self.currency, '')
        return f"{self.amount} {symbol}"
