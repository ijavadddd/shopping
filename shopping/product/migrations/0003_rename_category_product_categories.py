# Generated by Django 5.2 on 2025-04-13 12:51

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('product', '0002_remove_product_category_product_category'),
    ]

    operations = [
        migrations.RenameField(
            model_name='product',
            old_name='category',
            new_name='categories',
        ),
    ]
