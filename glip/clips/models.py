from django.contrib.auth import get_user_model
from django.db import models

from glip.games.models import Game

User = get_user_model()


class Clip(models.Model):
    clip_twitch_id = models.CharField(max_length=255, unique=True, primary_key=True)
    url = models.URLField()
    embed_url = models.URLField()
    broadcaster_id = models.CharField(max_length=50)
    broadcaster_name = models.CharField(max_length=250)
    creator_id = models.CharField(max_length=50)
    creator_name = models.CharField(max_length=250)
    video_id = models.CharField(max_length=50)
    twitch_game_id = models.CharField(max_length=50)
    game = models.ForeignKey(Game, on_delete=models.CASCADE, blank=True, null=True)
    language = models.CharField(max_length=5)
    title = models.CharField(max_length=255)
    twitch_view_count = models.DecimalField(max_digits=10, decimal_places=0)
    glip_view_count = models.CharField(
        max_length=15, blank=True, null=True, db_index=True
    )
    created_at = models.DateTimeField(db_index=True)
    thumbnail_url = models.URLField()
    duration = models.CharField(max_length=10)
    likes = models.ManyToManyField(User, related_name="like", default=None, blank=True)
    like_count = models.BigIntegerField(default="0")
    disabled = models.BooleanField(default=False, db_index=True)
