# Generated by Django 2.2.6 on 2019-12-09 10:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('kiosk', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='signup',
            name='payment_plan_collected_at',
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]