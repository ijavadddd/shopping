# Generated by Django 5.2 on 2025-04-29 11:33

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("cart", "0004_alter_cartitem_variation"),
        ("order", "0003_alter_orderitem_variation"),
        ("product", "0004_alter_productattribute_unique_together_and_more"),
    ]

    operations = [
        migrations.DeleteModel(
            name="ProductAttribute",
        ),
        migrations.AlterUniqueTogether(
            name="productvariation",
            unique_together={("product", "attribute")},
        ),
    ]
