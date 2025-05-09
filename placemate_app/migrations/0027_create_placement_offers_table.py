# Generated by Django 4.2.19 on 2025-03-20 19:14

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('placemate_app', '0026_create_drive_students_table'),
    ]

    operations = [
        migrations.CreateModel(
            name='PlacementOffer',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('offer_date', models.DateTimeField()),
                ('package', models.FloatField()),
                ('status', models.CharField(choices=[('Offered', 'Offered'), ('Accepted', 'Accepted'), ('Declined', 'Declined')], default='Offered', max_length=10)),
                ('drive', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='placemate_app.placementdrive')),
                ('job', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='placemate_app.job')),
                ('student', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='placemate_app.student')),
            ],
            options={
                'db_table': 'placement_offers',
                'unique_together': {('student', 'job', 'drive')},
            },
        ),
    ]
