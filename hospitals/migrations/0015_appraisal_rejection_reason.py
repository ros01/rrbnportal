# Generated by Django 3.0.3 on 2025-01-16 21:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('hospitals', '0014_auto_20250109_1738'),
    ]

    operations = [
        migrations.AddField(
            model_name='appraisal',
            name='rejection_reason',
            field=models.TextField(blank=True, null=True),
        ),
    ]
