import environ
from django.contrib.auth import get_user_model
from django.shortcuts import render
from django.views import View
from rest_framework.decorators import api_view
from rest_framework.response import Response

from glip.users.tasks import save_user_followers
from glip.users.utils import get_clips_of_specific_channel, get_user_follows

env = environ.Env()

User = get_user_model()


class FollowsListView(View):
    template_name = "pages/followslist.html"
    context_object_name = "clips"

    def get(self, request):
        template_name = "pages/followslist.html"
        follows = get_user_follows(request)
        save_user_followers(request)
        return render(request, template_name, {"follows": follows})


follows_view = FollowsListView.as_view()


@api_view(["GET"])
def my_view(request):
    follows = get_user_follows(request)
    return Response(data=follows)


@api_view(["GET"])
def broadcaster_top_clips_view(request):
    clips = get_clips_of_specific_channel(request, 26261471)
    return Response(data=clips)
