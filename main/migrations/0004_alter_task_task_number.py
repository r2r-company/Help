# Generated by Django 5.1.3 on 2024-12-04 00:10

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0003_alter_taskperformer_status'),
    ]

    operations = [
        migrations.AlterField(
            model_name='task',
            name='task_number',
            field=models.CharField(blank=True, max_length=12, unique=True),
        ),
    ]