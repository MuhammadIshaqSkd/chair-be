# Generated by Django 5.1.4 on 2025-01-06 05:48

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('ad_listing', '0004_alter_adlistimage_options_alter_adlisting_options_and_more'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='adlistimage',
            options={'verbose_name': "Images d'annonce", 'verbose_name_plural': "Images d'annonces"},
        ),
        migrations.AlterModelOptions(
            name='adlisting',
            options={'verbose_name': 'Liste des annonces', 'verbose_name_plural': 'Liste des annonces'},
        ),
    ]