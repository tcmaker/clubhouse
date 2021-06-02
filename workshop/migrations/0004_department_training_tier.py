# Generated by Django 3.2.2 on 2021-05-24 23:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('workshop', '0003_department'),
    ]

    operations = [
        migrations.AddField(
            model_name='department',
            name='training_tier',
            field=models.CharField(choices=[('NONE', 'No special training requirements'), ('SOME', 'Some training required'), ('PER_TOOL', 'Must demonstrate tool proficiency'), ('ORIENTATION_REQUIRED', 'Area Orientation is mandatory')], default='NONE', max_length=50, verbose_name='Training Tier'),
        ),
    ]
