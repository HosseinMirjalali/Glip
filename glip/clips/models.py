from django.contrib.auth import get_user_model
from django.db import models

# from glip.users.models import User

User = get_user_model()


class Channels(models.Model):
    twitch_id = models.CharField(max_length=50)
    twitch_login = models.CharField(max_length=50)
    twitch_name = models.CharField(max_length=50)


class Game(models.Model):
    game_id = models.CharField(max_length=255, unique=True)
    name = models.CharField(max_length=255)
    box_art_url = models.TextField()


class GameFollow(models.Model):
    following = models.ForeignKey(
        User, related_name="who_follows_game", on_delete=models.CASCADE
    )
    followed = models.ForeignKey(
        Game, related_name="followed_game", on_delete=models.CASCADE
    )
    follow_time = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["following", "followed"], name="unique_followers"
            )
        ]

    def __unicode__(self):
        return str(self.follow_time)


class ChannelFollow(models.Model):
    following = models.ForeignKey(
        User, related_name="who_follows_channel", on_delete=models.CASCADE
    )
    followed = models.ForeignKey(
        Channels, related_name="followed_channel", on_delete=models.CASCADE
    )
    follow_time = models.DateTimeField(auto_now=True)

    def __unicode__(self):
        return str(self.follow_time)
