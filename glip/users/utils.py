import environ
import requests
from allauth.socialaccount.models import SocialAccount
from django.contrib.auth import get_user_model

User = get_user_model()

env = environ.Env()

bearer = env("bearer")
client_id = env("client_id")
headers = {"Authorization": "Bearer {}".format(bearer), "Client-ID": client_id}


def get_user_follows(request):
    user_twitch_id = SocialAccount.objects.get(user=request.user).uid
    follows_url = (
        "https://api.twitch.tv/helix/users/follows?from_id={}&first=100".format(
            user_twitch_id
        )
    )
    response_data = requests.get(follows_url, headers=headers)
    follows = response_data.json()["data"]
    return follows
