# Generated by Django 4.2.5 on 2023-10-17 22:44

import datetime
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('kanban', '0022_task_expected_hours'),
    ]

    operations = [
        migrations.AlterField(
            model_name='board',
            name='end_date',
            field=models.DateField(default=datetime.date(2023, 10, 25)),
        ),
        migrations.CreateModel(
            name='TimeSpent',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('start_time', models.DateTimeField(auto_now_add=True)),
                ('end_time', models.DateTimeField(blank=True, null=True)),
                ('hours_spent', models.IntegerField(default=0)),
                ('task', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='kanban.task')),
                ('user', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
