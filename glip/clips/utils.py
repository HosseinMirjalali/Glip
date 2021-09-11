from datetime import datetime, timedelta

import environ

from glip.clips.models import Clip

env = environ.Env()
client_id = env("TWITCH_CLIENT_ID")


def get_past_day():
    return datetime.now() - timedelta(days=1)


def update_view_counts(clips: dict):
    for clip in clips:
        Clip.objects.filter(clip_twitch_id=clip["id"]).update(
            twitch_view_count=clip["view_count"]
        )
    pass
