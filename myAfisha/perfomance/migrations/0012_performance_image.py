# Generated by Django 5.1.6 on 2025-05-12 19:51

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('perfomance', '0011_remove_performance_hall'),
    ]

    operations = [
        migrations.AddField(
            model_name='performance',
            name='image',
            field=models.ImageField(blank=True, null=True, upload_to='performances/', verbose_name='Изображение'),
        ),
    ]
