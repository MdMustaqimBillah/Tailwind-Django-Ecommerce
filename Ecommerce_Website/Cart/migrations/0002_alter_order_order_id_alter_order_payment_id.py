# Generated by Django 5.1.3 on 2025-02-02 10:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Cart', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='order',
            name='order_id',
            field=models.CharField(blank=True, max_length=1024, null=True),
        ),
        migrations.AlterField(
            model_name='order',
            name='payment_id',
            field=models.CharField(blank=True, max_length=1024, null=True),
        ),
    ]
