# Generated by Django 4.2.19 on 2025-04-11 04:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('placemate_app', '0041_added_description_in_company'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='companydrivejobs',
            unique_together=set(),
        ),
        migrations.AlterUniqueTogether(
            name='placementoffer',
            unique_together=set(),
        ),
        migrations.AddField(
            model_name='companydrivejobs',
            name='job_description',
            field=models.TextField(default='this is backend developer job'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='companydrivejobs',
            name='job_title',
            field=models.CharField(default='backend developer', max_length=255),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='companydrivejobs',
            name='posted_date',
            field=models.DateTimeField(auto_now_add=True, default='2025-04-08 14:30:00'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='companydrivejobs',
            name='updated_date',
            field=models.DateTimeField(auto_now=True),
        ),
        migrations.RemoveField(
            model_name='companydrivejobs',
            name='job',
        ),
        migrations.RemoveField(
            model_name='placementoffer',
            name='drive',
        ),
        migrations.RemoveField(
            model_name='placementoffer',
            name='job',
        ),
        migrations.DeleteModel(
            name='Job',
        ),
    ]
