from django.contrib.auth import get_user_model
from django.db import models
from django.utils import timezone

User = get_user_model()


class Game(models.Model):
    game_id = models.CharField(max_length=255, unique=True)
    name = models.CharField(max_length=255)
    box_art_url = models.TextField()
    last_queried_clips = models.DateTimeField(
        blank=True, null=True, default=timezone.now
    )
    last_tried_query = models.DateTimeField(blank=True, null=True, default=timezone.now)
    follows = models.ManyToManyField(
        User, related_name="follow", default=None, blank=True
    )

    def __str__(self):
        return f"{self.name}"


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
                fields=["following", "followed"], name="unique_game_follows"
            )
        ]

    def __unicode__(self):
        return str(self.follow_time)


class TopGame(models.Model):
    id = models.CharField(max_length=255, unique=True, primary_key=True)
    name = models.CharField(max_length=255)
    box_art_url = models.TextField()
    order = models.BigIntegerField(blank=True, null=True)
    last_queried_clips = models.DateTimeField(
        blank=True, null=True, default=timezone.now
    )
    last_tried_query = models.DateTimeField(blank=True, null=True, default=timezone.now)
