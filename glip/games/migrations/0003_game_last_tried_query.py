# Generated by Django 3.1.12 on 2021-09-19 18:08

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('games', '0002_game_last_queried_clips'),
    ]

    operations = [
        migrations.AddField(
            model_name='game',
            name='last_tried_query',
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]
