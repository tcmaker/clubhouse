# Generated by Django 3.0.7 on 2020-06-09 18:21

from django.db import migrations, models
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('signup', '0006_registration_uuid'),
    ]

    operations = [
        migrations.AlterField(
            model_name='registration',
            name='uuid',
            field=models.UUIDField(default=uuid.uuid4, editable=False, null=True, unique=True),
        ),
    ]