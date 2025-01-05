from django.contrib import admin
from .models import PaymentService, Payment

@admin.register(PaymentService)
class PaymentServiceAdmin(admin.ModelAdmin):
    list_display = ('name', 'link', 'login')

@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ('service', 'current_payment_date', 'next_payment_date', 'amount')
    list_filter = ('service', 'current_payment_date', 'next_payment_date')
