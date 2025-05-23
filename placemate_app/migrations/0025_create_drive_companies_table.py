# Generated by Django 4.2.19 on 2025-03-20 19:07

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('placemate_app', '0024_create_placement_drives_table'),
    ]

    operations = [
        migrations.CreateModel(
            name='DriveCompany',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('company', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='placemate_app.company')),
                ('drive', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='placemate_app.placementdrive')),
            ],
            options={
                'db_table': 'drive_companies',
                'unique_together': {('drive', 'company')},
            },
        ),
    ]
