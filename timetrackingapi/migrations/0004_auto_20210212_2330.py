# Generated by Django 3.1.6 on 2021-02-12 21:30

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('timetrackingapi', '0003_auto_20210211_2338'),
    ]

    operations = [
        migrations.RenameField(
            model_name='vacation',
            old_name='vacation_end_date',
            new_name='end_date',
        ),
        migrations.RenameField(
            model_name='vacation',
            old_name='vacation_start_date',
            new_name='start_date',
        ),
    ]
