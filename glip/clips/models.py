from django.db import models


class Channels(models.Model):
    twitch_id = models.CharField(max_length=50)
    twitch_login = models.CharField(max_length=50)
    twitch_name = models.CharField(max_length=50)


class Game(models.Model):
    game_id = models.CharField(max_length=255, unique=True)
    name = models.CharField(max_length=255)
    box_art_url = models.TextField()
