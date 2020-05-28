# Generated by Django 3.0.6 on 2020-05-22 22:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('timeslots', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='timeslot',
            name='is_closed_by_staff',
            field=models.BooleanField(default=False, verbose_name='Area is closed for class or maintenance'),
        ),
    ]