# Generated by Django 4.0.5 on 2024-08-28 22:14

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('tasks', '0003_task_price_task_tip'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='task',
            name='price',
        ),
    ]
