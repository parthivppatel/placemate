# Generated by Django 4.2.19 on 2025-04-11 23:16

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('placemate_app', '0043_add_companyDrive_mapping_in_placementoffer_table'),
    ]

    operations = [
        migrations.AlterModelTable(
            name='companydrive',
            table='company_drives',
        ),
    ]
