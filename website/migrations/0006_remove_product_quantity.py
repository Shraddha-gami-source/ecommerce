# Generated by Django 3.0.8 on 2020-07-20 10:07

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('website', '0005_product_quantity'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='product',
            name='quantity',
        ),
    ]