# Generated by Django 3.1.12 on 2021-07-13 10:20

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('clips', '0002_game'),
    ]

    operations = [
        migrations.AlterField(
            model_name='game',
            name='game_id',
            field=models.CharField(max_length=255, unique=True),
        ),
    ]
