from concurrent.futures import as_completed
from datetime import datetime, timedelta, tzinfo

import environ
import requests
from allauth.socialaccount.models import SocialAccount, SocialToken
from django.contrib.auth import get_user_model
from requests_futures.sessions import FuturesSession

from glip.clips.models import Game, GameFollow
from glip.users.views import get_new_access_from_refresh

ZERO = timedelta(0)


class UTC(tzinfo):
    def utcoffset(self, dt):
        return ZERO

    def tzname(self, dt):
        return "UTC"

    def dst(self, dt):
        return ZERO


utc = UTC()
User = get_user_model()

env = environ.Env()

# bearer = ""
# change comment based on env
client_id = env("TWITCH_CLIENT_ID")
# client_id = SocialApp.objects.get(provider__iexact="twitch").client_id

# headers = {"Authorization": "Bearer {}".format(bearer), "Client-ID": client_id}
pnow = datetime.now(utc)
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


def user_login_maker(bulk_id_for_live):
    query_ids: str = ""
    if len(bulk_id_for_live) == 1:
        query_ids = "?id=" + bulk_id_for_live
    for single_id in bulk_id_for_live:
        query_ids = "?id=" + bulk_id_for_live[0]
        bulk_id_for_live.pop(0)
        query_ids.join(single_id)
    print("/////////////////////////////////////////////////////")
    print(query_ids)
    return query_ids


def get_user_bulk_info(broadcasters_id, request):
    payload = {"id": [broadcasters_id]}
    payload2 = {"user_id": [broadcasters_id]}
    bearer = "Bearer {}".format(get_token(request))
    headers = {"Authorization": "{}".format(bearer), "Client-ID": client_id}
    broadcaster_info_url = "https://api.twitch.tv/helix/users?"
    # streams_data_url = "https://api.twitch.tv/helix/streams?user_login="
    response_data = requests.get(broadcaster_info_url, headers=headers, params=payload)
    # print(response_data.json())
    bulk_info_pre_live = response_data.json()["data"]
    live_data = requests.get(
        "https://api.twitch.tv/helix/streams?", headers=headers, params=payload2
    )
    # print("@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@")
    # print(live_data)
    live_data2 = live_data.json()
    for data in live_data2["data"]:
        for infor in bulk_info_pre_live:
            if data["user_id"] == infor["id"]:
                infor["type"] = data["type"]
                infor["title"] = data["title"]
                infor["viewer_count"] = data["viewer_count"]
                infor["game_name"] = data["game_name"]
                print(infor)
    # futures = [
    #     session.get(
    #         'https://api.twitch.tv/helix/streams?user_login=' + i["login"], headers=headers
    #     )
    #     for i in bulk_info_pre_live
    # ]
    # for future in as_completed(futures):
    #     resp = future.result()
    #     print(resp.json())
    #     for i in resp.json()["data"]:
    #         bulk_info.append(i)

    return bulk_info_pre_live


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


def get_clips(request, broadcaster_id, first="1", date=formatted_past_day):
    """Get %first% clips of %broadcaster_id% from the past %date%"""
    bearer = "Bearer {}".format(get_token(request))
    headers = {"Authorization": "{}".format(bearer), "Client-ID": client_id}
    broadcaster_clip_url = "https://api.twitch.tv/helix/clips?broadcaster_id={}&first={}&started_at={}".format(
        broadcaster_id, first, date
    )
    response_data = requests.get(broadcaster_clip_url, headers=headers)
    if (
        response_data.status_code >= 400
    ):  # If the request gives error 401 due to expired token, it refreshes
        get_new_access_from_refresh(request)
        bearer = "Bearer {}".format(get_token(request))
        headers = {"Authorization": "{}".format(bearer), "Client-ID": client_id}
        response_data = requests.get(broadcaster_clip_url, headers=headers)
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
    clips = response_data.json()["data"]
    if (
        response_data.status_code >= 400
    ):  # If the request gives error 401 due to expired token, it refreshes
        get_new_access_from_refresh(request)
        bearer = "Bearer {}".format(get_token(request))
        headers = {"Authorization": "{}".format(bearer), "Client-ID": client_id}
        response_data = requests.get(broadcaster_clip_url, headers=headers)
        clips = response_data.json()["data"]
    return clips


def get_top_games(request):
    bearer = "Bearer {}".format(get_token(request))
    headers = {"Authorization": "{}".format(bearer), "Client-ID": client_id}
    first = 100
    top_games_url = "https://api.twitch.tv/helix/games/top?first={}".format(first)
    response_data = requests.get(top_games_url, headers=headers)
    if (
        response_data.status_code >= 400
    ):  # If the request gives error 401 due to expired token, it refreshes
        get_new_access_from_refresh(request)
        bearer = "Bearer {}".format(get_token(request))
        headers = {"Authorization": "{}".format(bearer), "Client-ID": client_id}
        response_data = requests.get(top_games_url, headers=headers)
    # try:
    #     game_info = data.get("data", [])
    # except IndexError:
    #     raise OAuth2Error("Invalid data from Twitch API: %s" % data)
    #
    # if "box_art_url" not in game_info:
    #     raise OAuth2Error("Invalid data from Twitch API: %s" % game_info)
    games = response_data.json()["data"]
    objs = [
        Game(game_id=e["id"], name=e["name"], box_art_url=e["box_art_url"])
        for e in games
    ]
    Game.objects.bulk_create(objs, ignore_conflicts=True)
    return games


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


def get_followed_games_clips_async(request, user_token):
    session = FuturesSession()
    headers = {"Authorization": "Bearer {}".format(user_token), "Client-ID": client_id}
    followed_games_id = GameFollow.objects.filter(following=request.user).values_list(
        "followed__game_id", flat=True
    )
    clips_data = []
    futures = [
        session.get(
            f"https://api.twitch.tv/helix/clips?game_id={i}&first=100&started_at={formatted_past_day}",
            headers=headers,
        )
        for i in followed_games_id
    ]
    for future in as_completed(futures):
        resp = future.result()
        print(resp.json())
        for i in resp.json()["data"]:
            clips_data.append(i)

    return clips_data
