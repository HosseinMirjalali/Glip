from django.contrib.auth import get_user_model
from django.db import models

User = get_user_model()


class Channel(models.Model):
    twitch_id = models.CharField(max_length=50)
    twitch_login = models.CharField(max_length=50)
    twitch_name = models.CharField(max_length=50)


class ChannelFollow(models.Model):
    following = models.ForeignKey(
        User, related_name="who_follows_channel", on_delete=models.CASCADE
    )
    followed = models.ForeignKey(
        Channel, related_name="followed_channel", on_delete=models.CASCADE
    )
    follow_time = models.DateTimeField(auto_now=True)

    def __unicode__(self):
        return str(self.follow_time)
