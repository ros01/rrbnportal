# Generated by Django 3.0.3 on 2022-05-04 00:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0002_auto_20210420_1155'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='user',
            name='type',
        ),
        migrations.AddField(
            model_name='hospital',
            name='type',
            field=models.CharField(blank=True, max_length=100),
        ),
    ]