# Generated by Django 5.1.3 on 2025-01-05 13:03

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('payment', '0004_alter_payment_reminder_days'),
    ]

    operations = [
        migrations.AddField(
            model_name='payment',
            name='currency',
            field=models.CharField(choices=[('UAH', 'Гривня'), ('EUR', 'Євро'), ('USD', 'Долар США')], default='UAH', max_length=3),
        ),
    ]
