# Generated by Django 4.2.19 on 2025-03-19 18:39

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('placemate_app', '0006_create_countries_table'),
    ]

    operations = [
        migrations.CreateModel(
            name='State',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('statename', models.CharField(max_length=255)),
                ('country', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='states', to='placemate_app.country')),
            ],
            options={
                'db_table': 'States',
            },
        ),
    ]
