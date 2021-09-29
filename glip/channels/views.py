from datetime import datetime, timedelta

import environ
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, render
from django.views import View

from glip.clips.models import Clip
from glip.games.models import Game
from glip.users.utils import get_clips, get_user_bulk_info, get_user_follows

env = environ.Env()

User = get_user_model()

past_day = datetime.now() - timedelta(days=1)
formatted_past_day = past_day.isoformat()[:-3] + "Z"
client_id = env("TWITCH_CLIENT_ID")


class FollowsListView(LoginRequiredMixin, View):
    template_name = "pages/followslist.html"

    def get(self, request):
        """
        First gets the list of user follows from Twitch API.
        Then fills an empty list of the followed IDs.
        Checks if there are more than 100 followed streamers, calls API twice separately
        and gets a maximum of 200 full detail streamers and renders the template.
        """

        template_name = "pages/followslist.html"
        follows = get_user_follows(request)
        broadcasters_id = []
        bulk_info = []
        for follow in follows:
            e = follow["to_id"]
            broadcasters_id.append(e)
        if len(broadcasters_id) > 100:
            first_100 = broadcasters_id[:100]
            fh_info = get_user_bulk_info(first_100, request)
            for fh in fh_info:
                bulk_info.append(fh)
            last_100 = broadcasters_id[100:]
            lh_info = get_user_bulk_info(last_100, request)
            for lh in lh_info:
                bulk_info.append(lh)
        else:
            bulk_info = get_user_bulk_info(broadcasters_id, request)
        return render(
            request, template_name, {"follows": follows, "bulk_info": bulk_info}
        )


follows_view = FollowsListView.as_view()


# useless function as of yet, ignore!
@login_required
def follow_user(request, game_id):
    game_to_follow = get_object_or_404(Game, pk=game_id)
    user_profile = request.user
    data = {}
    if game_to_follow.objects.filter(id=game_id.id).following.exists():
        data["message"] = "You are already following this user."
    else:
        game_to_follow.objects.filter(game_id.id).add(user_profile)
        data["message"] = "You are now following {}".format(game_to_follow)
    return JsonResponse(data, safe=False)


@login_required(login_url="/accounts/login/")
def clip_page(request):
    template_name = "pages/clip.html"
    broadcaster_name = request.GET.get("name")
    if broadcaster_name:
        template_info = "Top clips of %s from the past 24 hours" % broadcaster_name
    else:
        template_info = "Top clips of the Twitch streamer you selected"
    broadcaster_id = request.GET.get("broadcaster_id")
    first = request.GET.get("first")
    clips = get_clips(request, broadcaster_id, first)
    context = {"clips": clips, "template_info": template_info}
    return render(request, template_name, context)


def local_game_clip_view(request):
    template_name = "pages/new_clip.html"
    broadcaster_name = request.GET.get("channel")
    print("@@@@@@@@@@@@@@@@@@@@@@@@@@")
    print(broadcaster_name)
    template_info = f"Top {broadcaster_name} Twitch clips"
    start = datetime.now() - timedelta(hours=24)
    end = datetime.now()
    clips = (
        Clip.objects.filter(broadcaster_name__iexact=broadcaster_name)
        .filter(created_at__range=[start, end])
        .order_by("-twitch_view_count")[:100]
    )
    context = {"clips": clips, "template_info": template_info}

    return render(request, template_name, context)
