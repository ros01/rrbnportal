# Generated by Django 3.0.3 on 2021-02-24 18:01

import datetime
from django.db import migrations, models
import multiselectfield.db.fields


class Migration(migrations.Migration):

    dependencies = [
        ('hospitals', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='document',
            name='equipment',
            field=multiselectfield.db.fields.MultiSelectField(choices=[('Ultrasound', 'Ultrasound'), ('Conventional X-ray', 'Conventional X-ray'), ('Conventional X-ray with Fluoroscopy', 'Conventional X-ray with Fluoroscopy'), ('CT Scan', 'CT Scan'), ('C-Arm/O-ARM', 'C-Arm/O-ARM'), ('MRI', 'MRI'), ('Mamography', 'Mamography'), ('Angiography', 'Angiography'), ('Dental X-ray', 'Dental X-ray'), ('Echocardiography', 'Echocardiography'), ('Radiotherapy', 'Radiotherapy'), ('Nuclear Medicine', 'Nuclear Medicine')], max_length=172),
        ),
        migrations.AlterField(
            model_name='license',
            name='expiry_date',
            field=models.DateField(default=datetime.date.today),
        ),
        migrations.AlterField(
            model_name='license',
            name='issue_date',
            field=models.DateField(default=datetime.date.today),
        ),
        migrations.AlterField(
            model_name='records',
            name='equipment',
            field=multiselectfield.db.fields.MultiSelectField(choices=[('Ultrasound', 'Ultrasound'), ('Conventional X-ray', 'Conventional X-ray'), ('Conventional X-ray with Fluoroscopy', 'Conventional X-ray with Fluoroscopy'), ('CT Scan', 'CT Scan'), ('C-Arm/O-ARM', 'C-Arm/O-ARM'), ('MRI', 'MRI'), ('Mamography', 'Mamography'), ('Angiography', 'Angiography'), ('Dental X-ray', 'Dental X-ray'), ('Echocardiography', 'Echocardiography'), ('Radiotherapy', 'Radiotherapy'), ('Nuclear Medicine', 'Nuclear Medicine')], max_length=172),
        ),
    ]