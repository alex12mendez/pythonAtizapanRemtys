# Generated by Django 5.2.1 on 2025-05-30 19:46

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tramites', '0002_alter_clasificaciontramites_imagen'),
    ]

    operations = [
        migrations.AlterField(
            model_name='clasificaciontramites',
            name='imagen',
            field=models.ImageField(blank=True, null=True, upload_to='imagenes/'),
        ),
        migrations.AlterModelTable(
            name='clasificaciontramites',
            table='clasificacion_tramites',
        ),
    ]
