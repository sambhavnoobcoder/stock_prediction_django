# Generated by Django 3.2.6 on 2023-05-21 05:35

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0002_auto_20230521_0524'),
    ]

    operations = [
        migrations.AlterField(
            model_name='stockprediction',
            name='prediction_result',
            field=models.FloatField(blank=True, null=True),
        ),
    ]