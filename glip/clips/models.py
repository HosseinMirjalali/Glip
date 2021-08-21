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


class Clip(models.Model):
    clip_twitch_id = models.CharField(max_length=255, unique=True)
    url = models.URLField()
    embed_url = models.URLField()
    broadcaster_id = models.CharField(max_length=50)
    broadcaster_name = models.CharField(max_length=250)
    creator_id = models.CharField(max_length=50)
    creator_name = models.CharField(max_length=250)
    video_id = models.CharField(max_length=50)
    game_id = models.CharField(max_length=50)
    game = models.ForeignKey(Game, on_delete=models.CASCADE, blank=True, null=True)
    language = models.CharField(max_length=5)
    title = models.CharField(max_length=255)
    twitch_view_count = models.CharField(max_length=15)
    glip_view_count = models.CharField(max_length=15, blank=True, null=True)
    created_at = models.DateTimeField()
    thumbnail_url = models.URLField()
    duration = models.CharField(max_length=10)
