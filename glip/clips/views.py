from concurrent.futures import as_completed
from datetime import datetime, timedelta

import environ
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render
from django.views import View
from requests_futures.sessions import FuturesSession

from glip.users.utils import (
    get_clips,
    get_followed_games_clips_async,
    get_token,
    get_user_follows,
    get_user_follows2,
    get_user_games_channels_clips,
    validate_token, get_past_day,
)
from glip.users.views import get_new_access_from_refresh

env = environ.Env()

User = get_user_model()

past_day = datetime.now() - timedelta(days=1)
formatted_past_day = past_day.isoformat()[:-3] + "Z"

client_id = env("TWITCH_CLIENT_ID")


class ClipsListView(LoginRequiredMixin, View):
    template_name = "pages/clips.html"
    context_object_name = "clips"

    def get(self, request):
        """
        Gets list of followed streamers and recursively calls the API with each followed ID
        """
        template_name = "pages/clips.html"
        follows = get_user_follows(request)
        clips_info = []
        for follow in follows:
            e = get_clips(follow["to_id"], request)
            clips_info.extend(e)

        return render(request, template_name, {"clips_info": clips_info})


clips_view = ClipsListView.as_view()


@login_required(login_url="/accounts/login/")
def your_clip_page(request):
    template_name = "pages/clip.html"
    user_token = get_token(request)
    if validate_token(token=user_token) is True:
        pass
    else:
        get_new_access_from_refresh(request)
        user_token = get_token(request)
    user_game_follows_clips = get_followed_games_clips_async(request, user_token)
    user_channel_follows = get_user_follows2(request, user_token)
    clips = get_user_games_channels_clips(user_game_follows_clips, user_channel_follows)
    return render(request, template_name, {"clips": clips})


def futures_followed_clips(request):
    session = FuturesSession()
    followed_ids = []
    clips_data = []

    user_token = get_token(request)
    bearer = "Bearer {}".format(user_token)
    headers = {"Authorization": "{}".format(bearer), "Client-ID": client_id}
    follows = get_user_follows2(request, user_token)
    formatted_past_24h = get_past_day().isoformat()[:-3] + "Z"

    for follow in follows:
        followed_ids.append(follow["to_id"])

    futures = [
        session.get(
            f"https://api.twitch.tv/helix/clips?broadcaster_id={i}&first=3&started_at={formatted_past_24h}",
            headers=headers,
        )
        for i in followed_ids
    ]

    for future in as_completed(futures):
        resp = future.result()
        for i in resp.json()["data"]:
            clips_data.append(i)

    return render(request, "pages/clip.html", {"clips": clips_data})
