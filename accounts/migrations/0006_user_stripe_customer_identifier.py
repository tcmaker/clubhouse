# Generated by Django 3.2 on 2021-05-07 01:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0005_auto_20210330_0240'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='stripe_customer_identifier',
            field=models.CharField(blank=True, max_length=100, null=True, verbose_name='Stripe customer identifier'),
        ),
    ]
