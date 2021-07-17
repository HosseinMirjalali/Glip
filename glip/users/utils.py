from datetime import datetime, timedelta

import environ
import requests
from allauth.socialaccount.models import SocialAccount, SocialApp, SocialToken
from django.contrib.auth import get_user_model

from glip.clips.models import Game, GameFollow

User = get_user_model()

env = environ.Env()

# bearer = ""
# change comment based on env
# client_id = env("TWITCH_CLIENT_ID")
client_id = SocialApp.objects.get(provider__iexact="twitch").client_id

# headers = {"Authorization": "Bearer {}".format(bearer), "Client-ID": client_id}
now = datetime.utcnow().isoformat()[:-3] + "Z"
last_week = datetime.now() - timedelta(weeks=1)
formatted_last_week = last_week.isoformat()[:-3] + "Z"
past_day = datetime.now() - timedelta(days=1)
formatted_past_day = past_day.isoformat()[:-3] + "Z"


def get_token(request):
    account = SocialAccount.objects.get(user=request.user)
    st = SocialToken.objects.get(account=account)
    return st.token


def get_formatted_time(time_unit, num):
    past_timedelta = datetime.now() - timedelta(**{time_unit: num})
    formatted_time = past_timedelta.isoformat()[:3] + "Z"
    return formatted_time


def get_user_follows(request):
    """Get a list of user's followed channels on Twitch from Twitch API, first 200"""
    bearer = "Bearer {}".format(get_token(request))
    headers = {"Authorization": "{}".format(bearer), "Client-ID": client_id}
    user_twitch_id = SocialAccount.objects.get(user=request.user).uid
    follows_url = (
        "https://api.twitch.tv/helix/users/follows?from_id={}&first=100".format(
            user_twitch_id
        )
    )
    response_data = requests.get(follows_url, headers=headers)
    follows = response_data.json()["data"]
    r = response_data.json()
    # If condition that looks for the value 'cursor' in the response JSON and if it exists,
    # makes a second request to Twitch API and retrieves the next 100 follows
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


def get_user_follows2(request, user_token):
    """Get a list of user's followed channels on Twitch from Twitch API, first 200 second iteration"""
    bearer = "Bearer {}".format(user_token)
    headers = {"Authorization": "{}".format(bearer), "Client-ID": client_id}
    user_twitch_id = SocialAccount.objects.get(user=request.user).uid
    follows_url = (
        "https://api.twitch.tv/helix/users/follows?from_id={}&first=100".format(
            user_twitch_id
        )
    )
    response_data = requests.get(follows_url, headers=headers)
    follows = response_data.json()["data"]
    r = response_data.json()
    # If condition that looks for the value 'cursor' in the response JSON and if it exists,
    # makes a second request to Twitch API and retrieves the next 100 follows
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


def get_user_info(broadcaster_id, request):
    """Get full information of %broadcaster_id% channel"""
    bearer = "Bearer {}".format(get_token(request))
    headers = {"Authorization": "{}".format(bearer), "Client-ID": client_id}
    broadcaster_clip_url = "https://api.twitch.tv/helix/users?id={}".format(
        broadcaster_id
    )
    response_data = requests.get(broadcaster_clip_url, headers=headers)
    info = response_data.json()["data"]
    return info


def get_user_bulk_info(broadcasters_id, request):
    payload = {"id": [broadcasters_id]}
    bearer = "Bearer {}".format(get_token(request))
    headers = {"Authorization": "{}".format(bearer), "Client-ID": client_id}
    broadcaster_clip_url = "https://api.twitch.tv/helix/users?"
    response_data = requests.get(broadcaster_clip_url, headers=headers, params=payload)
    bulk_info = response_data.json()["data"]
    return bulk_info


def get_clips_of_specific_channel(broadcaster_id, request):
    """Get 3 most watched clips of a streamer from the past week"""
    bearer = "bearer {}".format(get_token(request))
    headers = {"Authorization": "Bearer {}".format(bearer), "Client-ID": client_id}
    broadcaster_clip_url = "https://api.twitch.tv/helix/clips?broadcaster_id={}&first=3&started_at={}".format(
        broadcaster_id, formatted_last_week
    )
    response_data = requests.get(broadcaster_clip_url, headers=headers)
    print(response_data)
    clips = response_data.json()["data"]
    return clips


def get_clips(request, broadcaster_id, first="1", date=formatted_last_week):
    """Get %first% clips of %broadcaster_id% from the past %date%"""
    bearer = "Bearer {}".format(get_token(request))
    headers = {"Authorization": "{}".format(bearer), "Client-ID": client_id}
    broadcaster_clip_url = "https://api.twitch.tv/helix/clips?broadcaster_id={}&first={}&started_at={}".format(
        broadcaster_id, first, date
    )
    response_data = requests.get(broadcaster_clip_url, headers=headers)
    print(response_data)
    clips = response_data.json()["data"]
    return clips


def get_clips_by_game(
    request, game_id, user_token, first="100", time_unit="days", num="1"
):
    """Get %first% clips of %game_id% from the past %num% %time_unit%
    TODO
    """
    bearer = "Bearer {}".format(user_token)
    headers = {"Authorization": "{}".format(bearer), "Client-ID": client_id}
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


def get_top_games(request):
    bearer = "Bearer {}".format(get_token(request))
    headers = {"Authorization": "{}".format(bearer), "Client-ID": client_id}
    first = 100
    top_games_url = "https://api.twitch.tv/helix/games/top?first={}".format(first)
    response_data = requests.get(top_games_url, headers=headers)
    games = response_data.json()["data"]
    objs = [
        Game(game_id=e["id"], name=e["name"], box_art_url=e["box_art_url"])
        for e in games
    ]
    Game.objects.bulk_create(objs, ignore_conflicts=True)
    return games


# Function not working/implemented yet


def get_user_games_channels_clips(user_game_follows_clips, user_channel_follows):
    print(user_game_follows_clips)
    chosen_clips = []
    user_game_follows_clips_broadcasters_id = (
        []
    )  # list of broadcaster IDs of user_game_follows_clips
    user_channel_follows_id = []  # list of IDs of user_channel_follows
    chosen_broadcaster_id = []
    for clip in user_game_follows_clips:
        user_game_follows_clips_broadcasters_id.append(clip["broadcaster_id"])
    for broadcaster in user_channel_follows:
        user_channel_follows_id.append(broadcaster["to_id"])
    for broadcaster_id in user_channel_follows_id:
        if broadcaster_id in user_game_follows_clips_broadcasters_id:
            chosen_broadcaster_id.append(broadcaster_id)
    for clip in user_game_follows_clips:
        if clip["broadcaster_id"] in chosen_broadcaster_id:
            chosen_clips.append(clip)
    return chosen_clips


def get_user_game_follows_clips(request, user_token):
    followed_games_id = GameFollow.objects.filter(following=request.user).values_list(
        "followed__game_id", flat=True
    )
    clips_info = []
    for game in followed_games_id:
        e = get_clips_by_game(request, game_id=game, user_token=user_token)
        clips_info.extend(e)
    return clips_info
