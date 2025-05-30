# Generated by Django 5.2 on 2025-04-29 11:26

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("product", "0002_remove_productattribute_price_modifier_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="productattribute",
            name="price_modifier",
            field=models.DecimalField(decimal_places=2, default=0.0, max_digits=10),
        ),
        migrations.AddField(
            model_name="productattribute",
            name="stock",
            field=models.PositiveIntegerField(default=0),
        ),
        migrations.DeleteModel(
            name="ProductVariation",
        ),
    ]
