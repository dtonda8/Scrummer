# Generated by Django 4.2.5 on 2023-10-19 06:26

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('kanban', '0024_delete_timespent'),
    ]

    operations = [
        migrations.AlterField(
            model_name='board',
            name='end_date',
            field=models.DateField(default=datetime.date(2023, 10, 26)),
        ),
    ]
