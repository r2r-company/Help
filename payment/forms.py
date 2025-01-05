from django import forms
from payment.models import Payment, PaymentService


class PaymentForm(forms.ModelForm):
    class Meta:
        model = Payment
        fields = ['current_payment_date', 'next_payment_date', 'amount', 'reminder_days', 'currency']
        widgets = {
            'current_payment_date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date',
                'placeholder': 'Введіть дату поточного платежу'
            }),
            'next_payment_date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date',
                'placeholder': 'Введіть дату наступного платежу'
            }),
            'amount': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Введіть суму платежу'
            }),
            'reminder_days': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Кількість днів до сповіщення'
            }),
            'currency': forms.Select(attrs={
                'class': 'form-control',
                'placeholder': 'Оберіть валюту'
            }),
        }


class PaymentServiceForm(forms.ModelForm):
    class Meta:
        model = PaymentService
        fields = ['name', 'link', 'login', 'password']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Назва сервісу'
            }),
            'link': forms.URLInput(attrs={
                'class': 'form-control',
                'placeholder': 'Посилання на сервіс'
            }),
            'login': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Логін для доступу'
            }),
            'password': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Пароль для доступу'
            }),
        }
