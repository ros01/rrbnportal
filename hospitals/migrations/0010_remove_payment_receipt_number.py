# Generated by Django 3.0.3 on 2024-12-29 03:13

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('hospitals', '0009_auto_20241206_1025'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='payment',
            name='receipt_number',
        ),
    ]
