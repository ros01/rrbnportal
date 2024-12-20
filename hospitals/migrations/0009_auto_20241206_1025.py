# Generated by Django 3.0.3 on 2024-12-06 10:25

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('hospitals', '0008_payment_rejection_reason'),
    ]

    operations = [
        migrations.AddField(
            model_name='payment',
            name='is_approved',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='payment',
            name='is_rejected',
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name='payment',
            name='rejection_reason',
            field=models.TextField(blank=True, null=True),
        ),
    ]
