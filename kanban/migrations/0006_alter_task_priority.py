# Generated by Django 4.2.5 on 2023-09-13 13:12

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('kanban', '0005_merge_20230912_1439'),
    ]

    operations = [
        migrations.AlterField(
            model_name='task',
            name='priority',
            field=models.CharField(choices=[('LW', 'Low'), ('MD', 'Medium'), ('IP', 'Important'), ('UR', 'Urgent'), ('IU', 'Important & Urgent')], default='MD', max_length=2),
        ),
    ]
