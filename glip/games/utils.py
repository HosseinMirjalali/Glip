from datetime import datetime, timedelta

import environ
import requests
from allauth.socialaccount.models import SocialApp
from django.core.exceptions import ObjectDoesNotExist

from glip.clips.models import Clip
from glip.clips.utils import update_view_counts, update_last_tried_date
from glip.games.models import Game

env = environ.Env()
client_id = env("TWITCH_CLIENT_ID")


def get_past_day():
    return datetime.now() - timedelta(days=1)


class MyException(Exception):
    pass


def get_and_save_games_clips(game_id):
    formatted_past_24h = get_past_day().isoformat()[:-3] + "Z"
    try:
        bearer = SocialApp.objects.get(provider__iexact="twitch").key
    except ObjectDoesNotExist:
        raise MyException("Twitch App is not added in admin panel.")

    bearer = "Bearer {}".format(bearer)
    headers = {"Authorization": "{}".format(bearer), "Client-ID": client_id}

    game_clip_url = (
        "https://api.twitch.tv/helix/clips?game_id={}&first={}&started_at={}".format(
            game_id, 100, formatted_past_24h
        )
    )
    response_data = requests.get(game_clip_url, headers=headers)
    try:
        clips = response_data.json()["data"]
    except KeyError:
        update_last_tried_date(game_id)
        return response_data.status_code, response_data.reason
    try:
        objs = [
            Clip(
                clip_twitch_id=c["id"],
                url=c["url"],
                embed_url=c["embed_url"],
                broadcaster_id=c["broadcaster_id"],
                broadcaster_name=c["broadcaster_name"],
                creator_id=c["creator_id"],
                creator_name=c["creator_name"],
                video_id=c["video_id"],
                twitch_game_id=c["game_id"],
                game=Game.objects.get(game_id__iexact=c["game_id"]),
                language=c["language"],
                title=c["title"],
                twitch_view_count=c["view_count"],
                # glip_view_count=c["created_at"],
                created_at=c["created_at"],
                thumbnail_url=c["thumbnail_url"],
                duration=c["duration"],
            )
            for c in clips
        ]
    except ObjectDoesNotExist:
        update_last_tried_date(game_id)
        print(f"@@@@@@@@@ Game field in Clip failed due to game id {game_id} not being found in Game table. @@@@@@@@@")
        return game_id
    Clip.objects.bulk_create(objs, ignore_conflicts=True)
    update_view_counts(clips)
    g = Game.objects.get(game_id=game_id)
    g.last_queried_clips = datetime.now()
    g.last_tried_query = datetime.now()
    g.save()

    return True
