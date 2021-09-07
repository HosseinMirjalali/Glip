# Generated by Django 3.1.12 on 2021-08-22 08:28

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Game',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('game_id', models.CharField(max_length=255, unique=True)),
                ('name', models.CharField(max_length=255)),
                ('box_art_url', models.TextField()),
            ],
        ),
        migrations.CreateModel(
            name='GameFollow',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('follow_time', models.DateTimeField(auto_now=True)),
                ('followed', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='followed_game', to='games.game')),
                ('following', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='who_follows_game', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.AddConstraint(
            model_name='gamefollow',
            constraint=models.UniqueConstraint(fields=('following', 'followed'), name='unique_game_follows'),
        ),
    ]