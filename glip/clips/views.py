import environ
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render
from django.views import View
from rest_framework.decorators import api_view
from rest_framework.response import Response

from glip.users.utils import (
    get_clips,
    get_clips_by_game,
    get_clips_of_specific_channel,
    get_user_bulk_info,
    get_user_follows,
)

env = environ.Env()

User = get_user_model()


class FollowsListView(LoginRequiredMixin, View):
    template_name = "pages/followslist.html"

    def get(self, request):
        template_name = "pages/followslist.html"
        follows = get_user_follows(request)
        broadcasters_id = []
        bulk_info = []
        for follow in follows:
            e = follow["to_id"]
            broadcasters_id.append(e)
        if len(broadcasters_id) > 100:
            first_100 = broadcasters_id[:100]
            fh_info = get_user_bulk_info(first_100)
            for fh in fh_info:
                bulk_info.append(fh)
            last_100 = broadcasters_id[100:]
            lh_info = get_user_bulk_info(last_100)
            for lh in lh_info:
                bulk_info.append(lh)
        else:
            bulk_info = get_user_bulk_info(broadcasters_id)
        return render(
            request, template_name, {"follows": follows, "bulk_info": bulk_info}
        )


follows_view = FollowsListView.as_view()


class ClipsListView(LoginRequiredMixin, View):
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


@login_required(login_url="/accounts/login/")
def clip_page(request):
    template_name = "pages/clip.html"
    broadcaster_id = request.GET.get("broadcaster_id")
    first = request.GET.get("first")
    clips = get_clips(broadcaster_id, first)
    return render(request, template_name, {"clips": clips})


@api_view(["GET"])
def my_view(request):
    follows = get_user_follows(request)
    return Response(data=follows)


@api_view(["GET"])
def broadcaster_top_clips_view(request):
    clips = get_clips_of_specific_channel(26261471)
    return Response(data=clips)


# @api_view(["GET"])
def game_top_clips_view(request):
    template_name = "pages/clip.html"
    clips = get_clips_by_game(21779, 20)
    return render(request, template_name, {"clips": clips})
    # return Response(data=clips)


@api_view(["GET"])
def broadcasters_info(request):
    follows = get_user_follows(request)
    broadcasters_id = []
    for follow in follows:
        e = follow["to_id"]
        broadcasters_id.append(e)
    bulk_info = get_user_bulk_info(broadcasters_id)
    return Response(data=bulk_info)
