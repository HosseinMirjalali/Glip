import json

import requests
from allauth.socialaccount.models import SocialAccount
from django.conf import settings
from django.contrib.auth import get_user_model
from django.http import JsonResponse
from requests import HTTPError

User = get_user_model()
bearer = "3btsxnw43jw95xzf823uwr5wesoui7"
profile_url = "https://api.twitch.tv/helix/users"
client_id = settings.SOCIALACCOUNT_PROVIDERS.get("client_id")


def get_clips(user_twitch_id):
    headers = {"Authorization": "Bearer {}".format(bearer), "Client-ID": client_id}
    clips_url = "https://api.twitch.tv/helix/users/follows?from_id={}".format(
        user_twitch_id
    )
    response = JsonResponse(requests.get(clips_url, headers=headers))
    print(response)
    # json.dumps(response)
    data = response.json()
    print(data)
    if response.status_code >= 400:
        error = data.get("error", "")
        message = data.get("message", "")
        raise HTTPError("error: %s (%s)" % (error, message))
    try:
        data.get("total", [])[0]
    except IndexError:
        raise ValueError("Invalid data: %s" % data)
    clips = json.loads(data)
    print(clips)
    return clips


def get_user_twitch_id(request):
    user = User.objects.get(request.user)
    print(user)
    return SocialAccount.objects.get(user=user).uid
