from django.db import models


class Channels(models.Model):
    twitch_id = models.CharField(max_length=50)
    twitch_login = models.CharField(max_length=50)
    twitch_name = models.CharField(max_length=50)
