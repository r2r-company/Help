from datetime import date, timedelta
from payment.models import Payment

def payment_notifications(request):
    today = date.today()

    # Майбутні платежі: від сьогодні до сьогодні + reminder_days
    upcoming_payments = [
        payment for payment in Payment.objects.all()
        if today <= payment.next_payment_date <= today + timedelta(days=payment.reminder_days)
    ]

    # Протерміновані платежі: дати, що минули до сьогодні
    overdue_payments = [
        payment for payment in Payment.objects.all()
        if payment.next_payment_date < today
    ]

    return {
        'upcoming_payment_count': len(upcoming_payments),
        'upcoming_payments': upcoming_payments,
        'overdue_payment_count': len(overdue_payments),
        'overdue_payments': overdue_payments,
    }
