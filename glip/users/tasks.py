import environ
import requests
from allauth.socialaccount.models import SocialAccount
from django.contrib.auth import get_user_model

from config import celery_app
from glip.clips.models import Channels

User = get_user_model()

env = environ.Env()


@celery_app.task()
def get_users_count():
    """A pointless Celery task to demonstrate usage."""
    return User.objects.count()


@celery_app.task()
def save_user_followers(request):
    bearer = env("bearer")
    client_id = env("client_id")
    headers = {"Authorization": "Bearer {}".format(bearer), "Client-ID": client_id}
    user_twitch_id = SocialAccount.objects.get(user=request.user).uid
    user = User.objects.get(username=request.user.username)
    clips_url = "https://api.twitch.tv/helix/users/follows?from_id={}&first=100".format(
        user_twitch_id
    )
    response_data = requests.get(clips_url, headers=headers)
    follows = response_data.json()["data"]

    for i in follows:
        user.follows = i["to_id"]
        c = Channels(
            twitch_id=i["to_id"],
            twitch_login=i["to_login"],
            twitch_name=i["to_name"],
        )
        c.save()
        user.channels.add(c)
