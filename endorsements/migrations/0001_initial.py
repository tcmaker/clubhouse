# Generated by Django 2.2.6 on 2019-12-10 05:10

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Capability',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50)),
                ('short_description', models.CharField(max_length=255)),
                ('long_description', models.TextField()),
            ],
        ),
        migrations.CreateModel(
            name='Endorsement',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('notes', models.TextField(blank=True, help_text='Only staff will be able to view these notes', null=True, verbose_name='Notes')),
                ('capability', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='endorsements.Capability')),
                ('recipient', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='recipient_set', to=settings.AUTH_USER_MODEL)),
                ('trainer', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='trainer_set', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.AddField(
            model_name='capability',
            name='recipients',
            field=models.ManyToManyField(through='endorsements.Endorsement', to=settings.AUTH_USER_MODEL),
        ),
    ]
