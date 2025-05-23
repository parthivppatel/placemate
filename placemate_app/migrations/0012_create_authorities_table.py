# Generated by Django 4.2.19 on 2025-03-20 15:53

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('placemate_app', '0011_create_placement_cell_members_table'),
    ]

    operations = [
        migrations.CreateModel(
            name='Authority',
            fields=[
                ('id', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, primary_key=True, serialize=False, to='placemate_app.user')),
                ('name', models.CharField(max_length=255)),
                ('designation', models.CharField(choices=[('Placement Officer', 'Placement Officer'), ('Assistant Placement Officer', 'Assistant Placement Officer')], default='Assistant Placement Officer', max_length=30)),
                ('qualification', models.CharField(max_length=255)),
                ('profile', models.CharField(max_length=255)),
                ('address', models.TextField()),
                ('branch', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='placemate_app.branch')),
            ],
            options={
                'db_table': 'authorities',
            },
        ),
    ]
