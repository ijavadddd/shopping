# Generated by Django 5.2 on 2025-04-19 07:10

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('cart', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='item',
            name='price',
        ),
    ]
