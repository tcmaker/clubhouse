# Generated by Django 3.0.6 on 2020-06-05 20:56

from django.db import migrations, models
import localflavor.us.models
import phonenumber_field.modelfields


class Migration(migrations.Migration):

    dependencies = [
        ('signup', '0002_auto_20200605_1232'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='registration',
            options={},
        ),
        migrations.AddField(
            model_name='invitation',
            name='address_city',
            field=models.CharField(blank=True, max_length=100, null=True, verbose_name='City'),
        ),
        migrations.AddField(
            model_name='invitation',
            name='address_state',
            field=localflavor.us.models.USStateField(blank=True, max_length=2, null=True, verbose_name='State'),
        ),
        migrations.AddField(
            model_name='invitation',
            name='address_street1',
            field=models.CharField(blank=True, max_length=100, null=True, verbose_name='Street Address'),
        ),
        migrations.AddField(
            model_name='invitation',
            name='address_street2',
            field=models.CharField(blank=True, max_length=100, null=True, verbose_name='Street Address 2'),
        ),
        migrations.AddField(
            model_name='invitation',
            name='address_zip',
            field=localflavor.us.models.USZipCodeField(blank=True, max_length=10, null=True, verbose_name='Zip Code'),
        ),
        migrations.AddField(
            model_name='invitation',
            name='emergency_contact_name',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
        migrations.AddField(
            model_name='invitation',
            name='emergency_contact_phone',
            field=phonenumber_field.modelfields.PhoneNumberField(blank=True, max_length=128, null=True, region=None),
        ),
        migrations.AddField(
            model_name='invitation',
            name='phone_can_receive_sms',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='invitation',
            name='phone_number',
            field=phonenumber_field.modelfields.PhoneNumberField(blank=True, max_length=128, null=True, region=None),
        ),
        migrations.AddField(
            model_name='registration',
            name='address_city',
            field=models.CharField(blank=True, max_length=100, null=True, verbose_name='City'),
        ),
        migrations.AddField(
            model_name='registration',
            name='address_state',
            field=localflavor.us.models.USStateField(blank=True, max_length=2, null=True, verbose_name='State'),
        ),
        migrations.AddField(
            model_name='registration',
            name='address_street1',
            field=models.CharField(blank=True, max_length=100, null=True, verbose_name='Street Address'),
        ),
        migrations.AddField(
            model_name='registration',
            name='address_street2',
            field=models.CharField(blank=True, max_length=100, null=True, verbose_name='Street Address 2'),
        ),
        migrations.AddField(
            model_name='registration',
            name='address_zip',
            field=localflavor.us.models.USZipCodeField(blank=True, max_length=10, null=True, verbose_name='Zip Code'),
        ),
        migrations.AddField(
            model_name='registration',
            name='emergency_contact_name',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
        migrations.AddField(
            model_name='registration',
            name='emergency_contact_phone',
            field=phonenumber_field.modelfields.PhoneNumberField(blank=True, max_length=128, null=True, region=None),
        ),
        migrations.AddField(
            model_name='registration',
            name='phone_can_receive_sms',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='registration',
            name='phone_number',
            field=phonenumber_field.modelfields.PhoneNumberField(blank=True, max_length=128, null=True, region=None),
        ),
    ]
