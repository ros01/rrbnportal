# Generated by Django 3.0.3 on 2022-05-07 01:33

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0003_auto_20220504_0000'),
    ]

    operations = [
        migrations.RenameField(
            model_name='hospital',
            old_name='reg_date',
            new_name='date',
        ),
    ]