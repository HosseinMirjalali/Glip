from concurrent.futures import as_completed
from datetime import datetime, timedelta

import environ
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Count
from django.http import Http404, HttpResponseRedirect
from django.http.response import JsonResponse
from django.shortcuts import get_object_or_404, render
from django.urls import reverse
from django.views import View
from requests_futures.sessions import FuturesSession

from glip.clips.models import Clip
from glip.comments.forms import NewCommentForm
from glip.games.models import GameFollow
from glip.users.utils import (
    get_clips,
    get_followed_games_clips_async,
    get_past_day,
    get_token,
    get_user_follows,
    get_user_follows2,
    get_user_games_channels_clips,
    validate_token,
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
    template_info = "Best clips of Twitch streamers and games you follow"
    user_token = get_token(request)
    if validate_token(token=user_token) is True:
        pass
    else:
        get_new_access_from_refresh(request)
        user_token = get_token(request)
    user_game_follows_clips = get_followed_games_clips_async(request, user_token)
    user_channel_follows = get_user_follows2(request, user_token)
    clips = get_user_games_channels_clips(user_game_follows_clips, user_channel_follows)
    context = {"clips": clips, "template_info": template_info}
    return render(request, template_name, context)


@login_required(login_url="/accounts/login/")
def new_your_clips_local(request):
    template_name = "pages/new_clip.html"
    template_info = "Best clips of Twitch streamers and games you follow"
    user_token = get_token(request)
    if validate_token(token=user_token) is True:
        pass
    else:
        get_new_access_from_refresh(request)
        user_token = get_token(request)
    # time_threshold = datetime.now() - timedelta(hours=24)
    start = datetime.now() - timedelta(hours=24)
    end = datetime.now()
    # new_end = end + timedelta(days=1)
    followed_games_id = GameFollow.objects.filter(following=request.user).values_list(
        "followed__game_id", flat=True
    )
    user_channel_follows_id = []
    user_channel_follows = get_user_follows2(request, user_token)
    for broadcaster in user_channel_follows:
        user_channel_follows_id.append(broadcaster["to_id"])

    games_id_dic = []
    for game_id in followed_games_id:
        games_id_dic.append(game_id)
    clips = (
        Clip.objects.filter(twitch_game_id__in=games_id_dic)
        .filter(broadcaster_id__in=user_channel_follows_id)
        .filter(created_at__range=[start, end])
        .annotate(comment_count=Count("comments"))
    )
    context = {"clips": clips, "template_info": template_info}
    return render(request, template_name, context)


def feed_view(request):
    template_name = "pages/homepage.html"
    template_info = "Most watched clips of the past 24 hours"
    start = datetime.now() - timedelta(hours=24)
    end = datetime.now()
    # clips = Clip.objects.filter(created_at__range=[start, end]).order_by(
    #     "-twitch_view_count"
    # )[:100]
    # clips = Clip.objects.all().annotate(comment_count=Count('comments'),
    #                                     filter=Q(created_at__range=[start, end])).order_by("-twitch_view_count")[:100]
    clips = (
        Clip.objects.filter(created_at__range=[start, end])
        .annotate(comment_count=Count("comments"))
        .order_by("-twitch_view_count")[:100]
    )
    context = {"clips": clips, "template_info": template_info}

    return render(request, template_name, context)


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


class ClipsJsonListView(View):
    def get(self, request, *args, **kwargs):
        start = datetime.now() - timedelta(hours=24)
        end = datetime.now()
        print(kwargs)
        upper = kwargs.get("num_pics")
        upper = int(request.GET.get("upper"))
        lower = upper - 3
        # clips = list(Clip.objects.values(created_at__range=[start, end]).order_by(
        #     "-twitch_view_count")[lower:upper])
        clips = list(
            Clip.objects.filter(created_at__range=[start, end])
            .values()
            .order_by("-twitch_view_count")[lower:upper]
        )
        pics_size = len(Clip.objects.all())
        size = True if upper >= pics_size else False
        return JsonResponse({"data": clips, "max": size}, safe=False)


clips_json = ClipsJsonListView.as_view()


def local_clip_detail_page(request, pk):
    template_name = "pages/clip_detail.html"
    try:
        clip = get_object_or_404(Clip, clip_twitch_id=pk)
    except Http404:
        response = render(request, template_name)
        response.status_code = 404
        return response

    comments = clip.comments.all()
    template_info = f"{clip.title} from {clip.broadcaster_name} playing {clip.game}"
    user_comment = None

    if request.method == "POST":
        comment_form = NewCommentForm(request.POST)
        if comment_form.is_valid():
            user_comment = comment_form.save(commit=False)
            user_comment.clip = clip
            user_comment.user = request.user
            user_comment.save()
            clip_detail_url = reverse("clips:clip_detail", args=[pk])
            return HttpResponseRedirect(clip_detail_url)
    else:
        comment_form = NewCommentForm()

    context = {
        "clip": clip,
        "comments": comments,
        "template_info": template_info,
        "user_comment": user_comment,
        "comment_form": comment_form,
    }

    return render(request, template_name, context)
