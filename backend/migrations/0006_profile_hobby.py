# Generated by Django 4.1.2 on 2025-04-06 14:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('backend', '0005_debt'),
    ]

    operations = [
        migrations.AddField(
            model_name='profile',
            name='hobby',
            field=models.CharField(blank=True, max_length=60),
        ),
    ]
