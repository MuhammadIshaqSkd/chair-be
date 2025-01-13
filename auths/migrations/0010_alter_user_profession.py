# Generated by Django 5.1.4 on 2025-01-12 14:50

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('auths', '0009_remove_userbusinessprofile_business_description_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='profession',
            field=models.CharField(choices=[('barber', 'Barber'), ('beauticians', 'Beauticians'), ('hair-dresser', 'Hair Dresser'), ('tattoo-artists', 'Tattoo Artists')], max_length=255, verbose_name='Profession', default='barber'),
        ),
    ]
