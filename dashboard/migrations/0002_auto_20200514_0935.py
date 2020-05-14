# Generated by Django 3.0.6 on 2020-05-14 09:35

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dashboard', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='civicrm_identifier',
            field=models.PositiveIntegerField(blank=True, null=True, verbose_name='identifier in civicrm'),
        ),
        migrations.AddField(
            model_name='user',
            name='sub',
            field=models.CharField(blank=True, max_length=100, null=True, unique=True, verbose_name='oidc identifier'),
        ),
    ]