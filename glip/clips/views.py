import environ
import requests
from allauth.socialaccount.models import SocialAccount
from django.contrib.auth import get_user_model
from django.shortcuts import render
from django.views import View
from rest_framework.decorators import api_view
from rest_framework.response import Response

env = environ.Env()

User = get_user_model()


class FollowsListView(View):
    template_name = "pages/followslist.html"
    context_object_name = "clips"

    def get(self, request):
        template_name = "pages/followslist.html"
        bearer = env("bearer")
        client_id = env("client_id")
        headers = {"Authorization": "Bearer {}".format(bearer), "Client-ID": client_id}
        user_twitch_id = SocialAccount.objects.get(user=request.user).uid
        clips_url = "https://api.twitch.tv/helix/users/follows?from_id={}".format(
            user_twitch_id
        )
        response_data = requests.get(clips_url, headers=headers)
        follows = response_data.json()["data"]
        return render(request, template_name, {"follows": follows})


follows_view = FollowsListView.as_view()


@api_view(["GET"])
def my_view(request):
    bearer = env("bearer")
    client_id = env("client_id")
    headers = {"Authorization": "Bearer {}".format(bearer), "Client-ID": client_id}
    user_twitch_id = SocialAccount.objects.get(user=request.user).uid
    clips_url = "https://api.twitch.tv/helix/users/follows?from_id={}".format(
        user_twitch_id
    )
    response_data = requests.get(clips_url, headers=headers)
    return Response(data=response_data.json())
