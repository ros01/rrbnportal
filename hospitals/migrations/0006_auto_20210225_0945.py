# Generated by Django 3.0.3 on 2021-02-25 09:45

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('hospitals', '0005_license_appraisal'),
    ]

    operations = [
        migrations.AlterField(
            model_name='license',
            name='appraisal',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='appraisal_15', to='hospitals.Appraisal'),
        ),
    ]