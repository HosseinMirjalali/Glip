from django.contrib.auth import get_user_model
from django.db import models

from glip.clips.models import Clip

User = get_user_model()


class Comment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    clip = models.ForeignKey(Clip, related_name="comments", on_delete=models.CASCADE)
    reply = models.ForeignKey(
        "self", null=True, related_name="replies", blank=True, on_delete=models.CASCADE
    )
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    likes = models.ManyToManyField(
        User, related_name="comment_like", default=None, blank=True
    )

    def __str__(self):
        return "%s - %s" % (self.clip.title, self.user)
