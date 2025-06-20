# Generated by Django 5.1.6 on 2025-04-23 13:17

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0005_hall'),
        ('perfomance', '0008_alter_performance_options_alter_performance_category_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='performanceschedule',
            name='hall',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='schedule', to='main.hall', verbose_name='Зал'),
        ),
        migrations.AddField(
            model_name='performanceschedule',
            name='theater',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='schedule', to='main.theater', verbose_name='Театр'),
        ),
    ]
