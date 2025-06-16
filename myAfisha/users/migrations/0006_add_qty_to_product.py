from django.db import migrations, models

class Migration(migrations.Migration):
    dependencies = [
        ('users', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='product',
            name='qty',
            field=models.PositiveIntegerField(default=0, verbose_name='Остаток на складе'),
        ),
    ]
