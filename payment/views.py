from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import DeleteView
from django.urls import reverse_lazy
from django.contrib import messages
from . import models
from .forms import PaymentServiceForm, PaymentForm
from .models import PaymentService, Payment
from datetime import date, timedelta


def payment_service_list(request):
    services = PaymentService.objects.all()
    return render(request, 'payment/payment_service_list.html', {'services': services})


def payment_service_detail(request, pk):
    service = get_object_or_404(PaymentService, pk=pk)
    payments = Payment.objects.filter(service=service)
    return render(request, 'payment/payment_service_detail.html', {
        'service': service,
        'payments': payments,
    })


def create_payment_service(request):
    if request.method == 'POST':
        form = PaymentServiceForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('payment_service_list')
    else:
        form = PaymentServiceForm()
    return render(request, 'payment/create_payment_service.html', {'form': form})


def create_payment(request, service_id):
    service = get_object_or_404(PaymentService, pk=service_id)
    if request.method == 'POST':
        form = PaymentForm(request.POST)
        if form.is_valid():
            payment = form.save(commit=False)
            payment.service = service
            payment.save()
            return redirect('payment_service_detail', pk=service.id)
    else:
        form = PaymentForm()
    return render(request, 'payment/create_payment.html', {'form': form, 'service': service})



def get_payment_notifications():
    """
    Отримує кількість платежів, які наближаються до дати сповіщення.
    """
    today = date.today()
    upcoming_payments = Payment.objects.filter(
        next_payment_date__lte=today + timedelta(days=models.F('reminder_days')),
        next_payment_date__gte=today  # Платежі, які ще не пропущені
    )
    return upcoming_payments.count()

class PaymentServiceDeleteView(DeleteView):
    model = PaymentService
    template_name = 'payment/payment_service_confirm_delete.html'
    success_url = reverse_lazy('payment_service_list')

def delete_payment(request, pk):
    payment = get_object_or_404(Payment, pk=pk)
    if request.method == 'POST':
        payment.delete()
        messages.success(request, 'Платіж успішно видалено.')
        return redirect('payment_service_list')
    return render(request, 'payment/payment_confirm_delete.html', {'payment': payment})