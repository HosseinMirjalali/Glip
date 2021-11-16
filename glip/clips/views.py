import os
from concurrent.futures import as_completed
from datetime import datetime, timedelta

import environ
import youtube_dl
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Count, Exists, OuterRef
from django.http import Http404, HttpResponse, HttpResponseRedirect
from django.http.response import JsonResponse
from django.shortcuts import get_object_or_404, render
from django.urls import reverse
from django.views import View
from requests_futures.sessions import FuturesSession

from glip.clips.models import Clip, TopClip
from glip.comments.forms import NewCommentForm
from glip.games.models import Game
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
    start = datetime.now() - timedelta(hours=24)
    end = datetime.now()
    followed_games_id = Game.objects.filter(follows=request.user).values_list(
        "game_id", flat=True
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
        .annotate(
            fav=Exists(User.objects.filter(like=OuterRef("pk"), id=request.user.id))
        )
        .annotate(comment_count=Count("comments"))
        .annotate(likes_count=Count("likes"))
        .exclude(disabled=True)
        .annotate(comment_count=Count("comments"))
        .order_by("-twitch_view_count")[:100]
    )
    context = {"clips": clips, "template_info": template_info}
    return render(request, template_name, context)


# @cache_page(60 * 15)
def feed_view(request):
    template_name = "pages/homepage.html"
    template_info = "Most watched clips of the past 24 hours"
    # clips = (
    #     Clip.objects.filter(created_at__range=[start, end])
    #     .annotate(comment_count=Count("comments"))
    #     .exclude(disabled=True)
    #     .order_by("-twitch_view_count")[:100]
    # )
    clips = []
    top_clips = (
        TopClip.objects.all()
        .select_related("clip")
        .annotate(comment_count=Count("clip__comments"))
        .annotate(likes_count=Count("clip__likes"))
        .annotate(
            fav=Exists(User.objects.filter(like=OuterRef("pk"), id=request.user.id))
        )
        .order_by("-clip__twitch_view_count")[:100]
    )

    for top_clip in top_clips:
        clip = top_clip.clip
        clip.comment_count = top_clip.comment_count
        clip.likes_count = top_clip.likes_count
        clip.fav = top_clip.fav
        clips.append(clip)
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

    comments = (
        clip.comments.all()
        .annotate(comment_like_count=Count("likes"))
        .annotate(
            comment_fav=Exists(
                User.objects.filter(comment_like=OuterRef("pk"), id=request.user.id)
            )
        )
    )
    template_info = f"{clip.title} from {clip.broadcaster_name} playing {clip.game}"
    user_comment = None
    fav = False

    try:
        user_id = request.user.id
        if clip.likes.filter(id=user_id).exists():
            fav = True
        else:
            fav = False
    except AttributeError:
        fav = False

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
        "fav": fav,
    }

    return render(request, template_name, context)


@login_required
def like_clip(request):
    if request.POST.get("action") == "post":
        result = ""
        clip_twitch_id = request.POST.get("clip_id")
        clip = get_object_or_404(Clip, clip_twitch_id=clip_twitch_id)
        if clip.likes.filter(id=request.user.id).exists():
            clip.likes.remove(request.user)
            clip.like_count -= 1
            result = clip.like_count
            clip.save()
        else:
            clip.likes.add(request.user)
            clip.like_count += 1
            result = clip.like_count
            clip.save()

        return JsonResponse({"result": result})


@login_required
def download_clip(request, pk):
    ydl_opts = {"outtmpl": f"{pk}.mp4"}
    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        ydl.download([f"https://clips.twitch.tv/{pk}"])

    path = f"{pk}.mp4"
    file_path = os.path.join(path)
    if os.path.exists(file_path):
        with open(file_path, "rb") as fh:
            response = HttpResponse(
                fh.read(), content_type="application/force-download"
            )
            response["Content-Disposition"] = "inline; filename=" + os.path.basename(
                file_path
            )
            os.remove(file_path)
            return response
    raise Http404

    # ydl_opts = {
    #     'outtmpl': '-'
    # }
    # with youtube_dl.YoutubeDL(ydl_opts) as ydl:
    #     sys.stdout = open('file', 'w')
    #     process = Popen(ydl.download([f"https://clips.twitch.tv/{pk}"]), stdout=PIPE)
    #     # response = FileResponse(process.stdout)
    #     response = StreamingHttpResponse(process.stdout)
    #     # file = ydl.download([f"https://clips.twitch.tv/{pk}"])
    #     return response
