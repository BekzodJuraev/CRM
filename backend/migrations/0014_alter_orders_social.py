# Generated by Django 4.2.4 on 2025-04-11 08:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('backend', '0013_remove_orders_category'),
    ]

    operations = [
        migrations.AlterField(
            model_name='orders',
            name='social',
            field=models.CharField(choices=[('social', 'Социальные сети'), ('cold_calls', 'Холодные звонки'), ('word_of_mouth', 'Сарафанное радио')], max_length=20),
        ),
    ]
