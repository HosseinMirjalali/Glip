import environ
from django.contrib.auth import get_user_model
from django.shortcuts import render
from django.views import View
from rest_framework.decorators import api_view
from rest_framework.response import Response

from glip.users.utils import (
    get_clips,
    get_clips_of_specific_channel,
    get_user_bulk_info,
    get_user_follows,
)

env = environ.Env()

User = get_user_model()


class FollowsListView(View):
    template_name = "pages/followslist.html"

    def get(self, request):
        template_name = "pages/followslist.html"
        follows = get_user_follows(request)
        broadcasters_id = []
        for follow in follows:
            e = follow["to_id"]
            broadcasters_id.append(e)
        bulk_info = get_user_bulk_info(broadcasters_id)
        return render(
            request, template_name, {"follows": follows, "bulk_info": bulk_info}
        )


follows_view = FollowsListView.as_view()


class ClipsListView(View):
    template_name = "pages/clips.html"
    context_object_name = "clips"

    def get(self, request):
        template_name = "pages/clips.html"
        follows = get_user_follows(request)
        clips_info = []
        for follow in follows:
            e = get_clips(follow["to_id"])
            clips_info.extend(e)

        return render(request, template_name, {"clips_info": clips_info})


clips_view = ClipsListView.as_view()


@api_view(["GET"])
def my_view(request):
    follows = get_user_follows(request)
    return Response(data=follows)


@api_view(["GET"])
def broadcaster_top_clips_view(request):
    clips = get_clips_of_specific_channel(26261471)
    return Response(data=clips)


@api_view(["GET"])
def broadcasters_info(request):
    follows = get_user_follows(request)
    broadcasters_id = []
    for follow in follows:
        e = follow["to_id"]
        broadcasters_id.append(e)
    bulk_info = get_user_bulk_info(broadcasters_id)
    return Response(data=bulk_info)
