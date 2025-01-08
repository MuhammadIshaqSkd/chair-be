# Generated by Django 5.1.4 on 2025-01-08 06:40

import django_uuid_upload
import functools
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('auths', '0004_alter_userbusinessprofile_options_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='profession',
            field=models.CharField(max_length=255, null=True, verbose_name='Profession'),
        ),
        migrations.AddField(
            model_name='userbusinessprofile',
            name='workspace',
            field=models.CharField(default=1, max_length=255, verbose_name='WorkSpace'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='userbusinessprofile',
            name='business_description',
            field=models.TextField(verbose_name='Business Description'),
        ),
        migrations.AlterField(
            model_name='userbusinessprofile',
            name='business_location',
            field=models.CharField(max_length=255, verbose_name='Business Location'),
        ),
        migrations.AlterField(
            model_name='userbusinessprofile',
            name='business_logo',
            field=models.ImageField(blank=True, null=True, upload_to=functools.partial(django_uuid_upload._upload_to_uuid_impl, *(), **{'make_dir': False, 'path': 'business_logos/', 'remove_qs': True}), verbose_name='Business Logo'),
        ),
        migrations.AlterField(
            model_name='userbusinessprofile',
            name='business_name',
            field=models.CharField(max_length=255, verbose_name='Business Name'),
        ),
        migrations.AlterField(
            model_name='userbusinessprofile',
            name='business_website',
            field=models.URLField(blank=True, max_length=255, null=True, verbose_name='Business Website'),
        ),
        migrations.AlterField(
            model_name='userbusinessprofile',
            name='total_ratings',
            field=models.FloatField(default=0.0, verbose_name='Total Rating'),
        ),
        migrations.AlterField(
            model_name='userbusinessprofile',
            name='total_reviews',
            field=models.IntegerField(default=0, verbose_name='Total Reviews'),
        ),
    ]