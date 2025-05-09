# Generated by Django 4.2.19 on 2025-03-20 15:41

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('placemate_app', '0010_create_courses_table'),
    ]

    operations = [
        migrations.CreateModel(
            name='PlacementCellMember',
            fields=[
                ('id', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, primary_key=True, serialize=False, to='placemate_app.user')),
                ('role_in_cell', models.CharField(choices=[('Head', 'Head'), ('Faculty Member', 'Faculty Member'), ('Student Coordinator', 'Student Coordinator'), ('Student Member', 'Student Member'), ('Placement Officer', 'Placement Officer'), ('Assistant Placement Officer', 'Assistant Placement Officer')], default='Student Member', max_length=30)),
                ('join_date', models.DateTimeField()),
                ('end_date', models.DateTimeField(blank=True, null=True)),
                ('active_status', models.BooleanField(default=True)),
                ('branch', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='placemate_app.branch')),
            ],
            options={
                'db_table': 'placement_cell_members',
            },
        ),
    ]
