# Generated by Django 3.0.3 on 2020-06-01 14:54

import datetime
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import multiselectfield.db.fields


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Registration',
            fields=[
                ('id', models.IntegerField(default=10000, max_length=6, primary_key=True, serialize=False, unique=True)),
                ('hospital_name', models.CharField(max_length=200)),
                ('license_category', models.CharField(max_length=200)),
                ('rc_number', models.CharField(max_length=100)),
                ('phone', models.CharField(max_length=100)),
                ('email', models.EmailField(max_length=100)),
                ('state', models.CharField(choices=[('Abia', 'Abia'), ('Adamawa', 'Adamawa'), ('Akwa Ibom', 'Akwa Ibom'), ('Anambra', 'Anambra'), ('Bauchi', 'Bauchi'), ('Bayelsa', 'Bayelsa'), ('Benue', 'Benue'), ('Borno', 'Borno'), ('Cross River', 'Cross River'), ('Delta', 'Delta'), ('Ebonyi', 'Ebonyi'), ('Enugu', 'Enugu'), ('Edo', 'Edo'), ('Ekiti', 'Ekiti'), ('FCT', 'FCT'), ('Gombe', 'Gombe'), ('Imo', 'Imo'), ('Jigawa', 'Jigawa'), ('Kaduna', 'Kaduna'), ('Kano', 'Kano'), ('Kebbi', 'Kebbi'), ('Kogi', 'Kogi'), ('Kwara', 'Kwara'), ('Lagos', 'Lagos'), ('Nasarawa', 'Nasarawa'), ('Niger', 'Niger'), ('Ogun', 'Ogun'), ('Ondo', 'Ondo'), ('Osun', 'Osun'), ('Oyo', 'Oyo'), ('Plateau', 'Plateau'), ('Rivers', 'Rivers'), ('Sokoto', 'Sokoto'), ('Taraba', 'Taraba'), ('Yobe', 'Yobe'), ('Zamfara', 'Zamfara')], max_length=100)),
                ('city', models.CharField(max_length=100)),
                ('address', models.CharField(max_length=200)),
                ('services', models.CharField(choices=[('Diagnostic Radiography', 'Diagnostic Radiography'), ('Therapeutic Radiography', 'Therapeutic Radiography')], max_length=100)),
                ('equipment', multiselectfield.db.fields.MultiSelectField(choices=[('Ultrasound', 'Ultrasound'), ('X-ray', 'X-ray'), ('CT Scan', 'CT Scan'), ('MRI', 'MRI'), ('Mamography', 'Mamography'), ('Angiography', 'Angiography'), ('Dental Radiography', 'Dental Radiography'), ('Echocardiography', 'Echocardiography'), ('Linac', 'Linac'), ('Cobalt 60', 'Cobalt 60'), ('Nuclear Medicine', 'Nuclear Medicine')], max_length=120)),
                ('radiographers', models.CharField(blank=True, max_length=200)),
                ('reg_date', models.DateTimeField(blank=True, default=datetime.datetime.now)),
                ('cac_certificate', models.ImageField(blank=True, upload_to='%Y/%m/%d/')),
                ('practice_license', models.ImageField(blank=True, upload_to='%Y/%m/%d/')),
                ('practice_manager', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Payment',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('application_no', models.CharField(max_length=200)),
                ('hospital_name', models.CharField(max_length=200)),
                ('license_category', models.CharField(max_length=200)),
                ('phone', models.CharField(max_length=100)),
                ('email', models.EmailField(max_length=100)),
                ('state', models.CharField(max_length=200)),
                ('city', models.CharField(max_length=100)),
                ('address', models.CharField(max_length=200)),
                ('services', models.CharField(max_length=200)),
                ('equipment', models.CharField(max_length=200)),
                ('radiographers', models.CharField(max_length=200)),
                ('rrr_number', models.CharField(max_length=100)),
                ('receipt_number', models.CharField(max_length=100)),
                ('payment_amount', models.CharField(max_length=100)),
                ('payment_method', models.CharField(choices=[('Bank', 'Bank')], max_length=10)),
                ('payment_receipt', models.FileField(blank=True, upload_to='%Y/%m/%d/')),
                ('payment_date', models.DateTimeField(blank=True, default=datetime.datetime.now)),
                ('vet_status', models.IntegerField(default=1)),
                ('practice_manager', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='License',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('application_no', models.CharField(max_length=100)),
                ('hospital_name', models.CharField(max_length=200)),
                ('license_category', models.CharField(max_length=200)),
                ('license_no', models.CharField(max_length=200)),
                ('address', models.CharField(max_length=200)),
                ('phone', models.CharField(max_length=100)),
                ('email', models.EmailField(max_length=100)),
                ('issue_date', models.DateTimeField(blank=True, default=datetime.datetime.now)),
                ('expiry_date', models.DateTimeField(blank=True, default=datetime.datetime.now)),
                ('validity', models.CharField(choices=[('Active', 'Active'), ('Expired', 'Expired')], max_length=10)),
                ('practice_manager', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Inspection',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('application_no', models.CharField(max_length=100)),
                ('hospital_name', models.CharField(max_length=200)),
                ('license_category', models.CharField(max_length=200)),
                ('address', models.CharField(max_length=200)),
                ('phone', models.CharField(max_length=100)),
                ('email', models.EmailField(max_length=100)),
                ('inspection_schedule_date', models.DateTimeField(blank=True, default=datetime.datetime.now)),
                ('inspection_date', models.DateTimeField(blank=True, default=datetime.datetime.now)),
                ('inspection_status', models.CharField(max_length=100)),
                ('shielding', models.IntegerField()),
                ('equipment', models.IntegerField()),
                ('radiographer_adequacy', models.IntegerField()),
                ('radiographer_license', models.IntegerField()),
                ('personnel_monitoring', models.IntegerField()),
                ('room_size', models.IntegerField()),
                ('water_supply', models.IntegerField()),
                ('C07_form', models.IntegerField()),
                ('darkroom', models.IntegerField()),
                ('safety', models.IntegerField()),
                ('photo_main', models.ImageField(blank=True, upload_to='media/%Y/%m/%d/')),
                ('photo_1', models.ImageField(blank=True, upload_to='media/%Y/%m/%d/')),
                ('photo_2', models.ImageField(blank=True, upload_to='media/%Y/%m/%d/')),
                ('photo_3', models.ImageField(blank=True, upload_to='media/%Y/%m/%d/')),
                ('photo_4', models.ImageField(blank=True, upload_to='media/%Y/%m/%d/')),
                ('photo_5', models.ImageField(blank=True, upload_to='media/%Y/%m/%d/')),
                ('photo_6', models.ImageField(blank=True, upload_to='media/%Y/%m/%d/')),
                ('practice_manager', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
