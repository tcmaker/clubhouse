# Generated by Django 2.2.6 on 2019-12-09 13:30

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Cubby',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('aisle', models.CharField(max_length=5)),
                ('identifier', models.CharField(max_length=5)),
                ('assignee', models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name_plural': 'cubbies',
            },
        ),
        migrations.CreateModel(
            name='GreenTag',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=100)),
                ('location', models.CharField(max_length=200)),
                ('issued_at', models.DateTimeField(default=django.utils.timezone.now)),
                ('description', models.TextField()),
                ('status', models.CharField(choices=[('active', 'Active'), ('expired', 'Expired'), ('noncompliant', 'Non-Compliant'), ('closed', 'Closed')], max_length=40)),
                ('assignee', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='green_tags_issued', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='RedTag',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=100)),
                ('location', models.CharField(max_length=200)),
                ('description', models.TextField()),
                ('issued_at', models.DateTimeField(default=django.utils.timezone.now)),
                ('violator_notified_at', models.DateTimeField(blank=True, null=True)),
                ('status', models.CharField(choices=[('reported', 'Reported'), ('verified', 'Verified'), ('invalid', 'Invalid'), ('resolved', 'Resolved')], max_length=40)),
                ('cubby', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='storage.Cubby')),
                ('green_tag', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='storage.GreenTag')),
                ('reporter', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='red_tags_created', to=settings.AUTH_USER_MODEL)),
                ('violator', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='red_tag_violations', to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]