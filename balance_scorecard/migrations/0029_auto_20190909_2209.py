# Generated by Django 2.1.8 on 2019-09-10 01:09

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('balance_scorecard', '0028_compromisos_id_incidente'),
    ]

    operations = [
        migrations.AlterField(
            model_name='reunion',
            name='fecha_reunion',
            field=models.DateField(unique=True),
        ),
    ]
