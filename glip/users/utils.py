from datetime import datetime, timedelta

import environ
import requests
from allauth.socialaccount.models import SocialAccount, SocialToken
from django.contrib.auth import get_user_model

User = get_user_model()

env = environ.Env()

bearer = env("bearer")
client_id = env("client_id")
headers = {"Authorization": "Bearer {}".format(bearer), "Client-ID": client_id}
now = datetime.utcnow().isoformat()[:-3] + "Z"
last_week = datetime.now() - timedelta(weeks=1)
formatted_last_week = last_week.isoformat()[:-3] + "Z"
past_day = datetime.now() - timedelta(days=1)
formatted_past_day = past_day.isoformat()[:-3] + "Z"


def get_formatted_time(time_unit, num):
    past_timedelta = datetime.now() - timedelta(**{time_unit: num})
    formatted_time = past_timedelta.isoformat()[:3] + "Z"
    return formatted_time


def get_user_twitch_token(request):
    user = request.user
    print("@@@@@@@@@@@@@@@@@@@@@@@@@@@@@")
    print(user)
    user_twitch_token = SocialToken.objects.filter(
        account__user=user, account__provider="twitch"
    )
    return user_twitch_token


def get_user_follows(request):
    """Get a list of user's followed channels on Twitch from Twitch API (first 100, no pagination)"""
    user_twitch_id = SocialAccount.objects.get(user=request.user).uid
    follows_url = (
        "https://api.twitch.tv/helix/users/follows?from_id={}&first=100".format(
            user_twitch_id
        )
    )
    response_data = requests.get(follows_url, headers=headers)
    follows = response_data.json()["data"]
    r = response_data.json()
    if "cursor" in r["pagination"]:
        cursor = response_data.json()["pagination"]["cursor"]
        rest = requests.get(
            "https://api.twitch.tv/helix/users/follows?after={}&from_id={}".format(
                cursor, user_twitch_id
            ),
            headers=headers,
        ).json()
        for r in rest["data"]:
            follows.append(r)
    else:
        pass
    return follows


def get_user_info(broadcaster_id):
    """Get full information of %broadcaster_id% channel"""
    broadcaster_clip_url = "https://api.twitch.tv/helix/users?id={}".format(
        broadcaster_id
    )
    response_data = requests.get(broadcaster_clip_url, headers=headers)
    info = response_data.json()["data"]
    return info


def get_user_bulk_info(broadcasters_id):
    payload = {"id": [broadcasters_id]}
    broadcaster_clip_url = "https://api.twitch.tv/helix/users?"
    response_data = requests.get(broadcaster_clip_url, headers=headers, params=payload)
    bulk_info = response_data.json()["data"]
    return bulk_info


def get_clips_of_specific_channel(broadcaster_id):
    """Get 3 most watched clips of a streamer from the past week"""
    broadcaster_clip_url = "https://api.twitch.tv/helix/clips?broadcaster_id={}&first=3&started_at={}".format(
        broadcaster_id, formatted_last_week
    )
    response_data = requests.get(broadcaster_clip_url, headers=headers)
    print(response_data)
    clips = response_data.json()["data"]
    return clips


def get_clips(broadcaster_id, first="1", date=formatted_last_week):
    """Get %first% clips of %broadcaster_id% from the past %date%"""
    broadcaster_clip_url = "https://api.twitch.tv/helix/clips?broadcaster_id={}&first={}&started_at={}".format(
        broadcaster_id, first, date
    )
    response_data = requests.get(broadcaster_clip_url, headers=headers)
    print(response_data)
    clips = response_data.json()["data"]
    return clips


def get_clips_by_game(game_id, first="30", time_unit="days", num="1"):
    """Get %first% clips of %game_id% from the past %num% %time_unit%"""
    # formatted_time = get_formatted_time(time_unit, num)
    broadcaster_clip_url = (
        "https://api.twitch.tv/helix/clips?game_id={}&first={}&started_at={}".format(
            game_id, first, formatted_past_day
        )
    )
    response_data = requests.get(broadcaster_clip_url, headers=headers)
    print(response_data)
    clips = response_data.json()["data"]
    return clips
