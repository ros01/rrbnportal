# Generated by Django 3.0.3 on 2024-11-19 15:10

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('hospitals', '0004_auto_20220508_1949'),
    ]

    operations = [
        migrations.AddField(
            model_name='inspection',
            name='inspection_date',
            field=models.DateField(default=datetime.date.today),
        ),
        migrations.AlterField(
            model_name='schedule',
            name='inspection_zone',
            field=models.CharField(choices=[('Abuja', 'Abuja'), ('Enugu', 'Enugu'), ('Lagos', 'Lagos'), ('Sokoto', 'Sokoto'), ('Kano', 'Kano'), ('Port Harcourt', 'Port Harcourt'), ('Awka', 'Awka'), ('Calabar', 'Calabar'), ('Ilesha', 'Ilesha'), ('Maiduguri', 'Maiduguri')], max_length=100),
        ),
    ]