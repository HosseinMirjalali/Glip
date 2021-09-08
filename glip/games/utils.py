from allauth.socialaccount.models import SocialApp
from django.core.exceptions import ObjectDoesNotExist
from datetime import datetime, timedelta
from django.utils import timezone
import environ
import requests

from glip.clips.api.serializers import ClipSerializer
from glip.clips.models import Clip
from glip.clips.utils import update_view_counts
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
        raise MyException('Twitch App is not added in admin panel.')

    bearer = "Bearer {}".format(bearer)
    headers = {"Authorization": "{}".format(bearer), "Client-ID": client_id}

    game_clip_url = (
        "https://api.twitch.tv/helix/clips?game_id={}&first={}&started_at={}".format(
            game_id, 100, formatted_past_24h
        )
    )
    response_data = requests.get(game_clip_url, headers=headers)
    clips = response_data.json()["data"]
    # update_view_counts(clips)
    # objs = [
    #     Clip(clip_twitch_id=c["id"],
    #          url=c["url"],
    #          embed_url=c["embed_url"],
    #          broadcaster_id=c["broadcaster_id"],
    #          broadcaster_name=c["broadcaster_name"],
    #          creator_id=c["creator_id"],
    #          creator_name=c["creator_name"],
    #          video_id=c["video_id"],
    #          twitch_game_id=c["game_id"],
    #          game=Game.objects.get(game_id__iexact=c["game_id"]),
    #          language=c["language"],
    #          title=c["title"],
    #          twitch_view_count=c["view_count"],
    #          # glip_view_count=c["created_at"],
    #          created_at=c["created_at"],
    #          thumbnail_url=c["thumbnail_url"],
    #          duration=c["duration"], )
    #     for c in clips
    # ]
    for clip in clips:
        clip["clip_twitch_id"] = clip["id"]
        del clip["id"]
        clip["twitch_game_id"] = clip["game_id"]
        del clip["game_id"]
        clip["twitch_view_count"] = clip["view_count"]
        del clip["view_count"]
        clip["game"] = Game.objects.get(game_id__iexact=game_id)
        Clip.objects.update_or_create(**clip)
    # serializer = ClipSerializer(data=new_clips, many=True)
    # serializer.is_valid(raise_exception=True)
    # serializer.save()
    # Clip.objects.bulk_create(new_clips, ignore_conflicts=True)
    g = Game.objects.get(game_id=game_id)
    g.last_queried_clips = timezone.now()
    g.save()

    return True


def new_get_and_save_game_clips(game: Game):
    formatted_past_24h = get_past_day().isoformat()[:-3] + "Z"
    try:
        bearer = SocialApp.objects.get(provider__iexact="twitch").key
    except ObjectDoesNotExist:
        raise MyException('Twitch App is not added in admin panel.')
    game_id = game.game_id
    bearer = "Bearer {}".format(bearer)
    headers = {"Authorization": "{}".format(bearer), "Client-ID": client_id}

    game_clip_url = (
        "https://api.twitch.tv/helix/clips?game_id={}&first={}&started_at={}".format(
            game_id, 100, formatted_past_24h
        )
    )
    response_data = requests.get(game_clip_url, headers=headers)
    clips = response_data.json()["data"]
    new_clips = []
    for clip in clips:
        clip["clip_twitch_id"] = clip["id"]
        del clip["id"]
        clip["twitch_game_id"] = clip["game_id"]
        del clip["game_id"]
        clip["twitch_view_count"] = clip["view_count"]
        del clip["view_count"]
        game = clip["game"]
        new_clips.append(clip)

        clip["clip_twitch_id"] = clip.pop("id")
        clip["twitch_game_id"] = clip.pop("game_id")
        clip["twitch_view_count"] = clip.pop("view_count")
        clip["game"] = game
        print(clip)

    print(new_clips)

    pass
