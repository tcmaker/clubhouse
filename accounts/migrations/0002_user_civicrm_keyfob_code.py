# Generated by Django 3.0.6 on 2020-05-15 10:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='civicrm_keyfob_code',
            field=models.CharField(blank=True, max_length=30, null=True, verbose_name='keyfob code from civicrm'),
        ),
    ]