import environ
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.views import View
from rest_framework.decorators import api_view
from rest_framework.response import Response

from glip.clips.models import Game, GameFollow
from glip.users.utils import (
    get_clips,
    get_clips_by_game,
    get_clips_of_specific_channel,
    get_token,
    get_top_games,
    get_user_bulk_info,
    get_user_follows,
    get_user_follows2,
    get_user_game_follows_clips,
    get_user_games_channels_clips,
)

env = environ.Env()

User = get_user_model()


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


class GamesListView(LoginRequiredMixin, View):
    template_name = "pages/games.html"
    context_object_name = "games"

    def get(self, request):
        """
        Gets list of followed streamers and recursively calls the API with each followed ID
        """
        template_name = "pages/games.html"
        games = get_top_games(request)
        followed_games = GameFollow.objects.filter(following=request.user).values_list(
            "followed__game_id", flat=True
        )
        print(followed_games)
        for game in games:
            game["box_art_url"] = game["box_art_url"].replace("{width}", "200")
            game["box_art_url"] = game["box_art_url"].replace("{height}", "200")
            if game["id"] in followed_games:
                game["is_followed"] = True
            else:
                game["is_followed"] = False
        context = {
            "followcheck": GameFollow.objects.filter(following=request.user),
            "games": games,
        }
        return render(request, template_name, context)


games_view = GamesListView.as_view()


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
def follow_game(request):
    game_id = request.GET.get("game_id")
    game_to_follow = Game.objects.get(game_id=game_id)
    user = request.user
    GameFollow.objects.get_or_create(following=user, followed=game_to_follow)
    return redirect(reverse("clips:games"))


@login_required(login_url="/accounts/login/")
def clip_page(request):
    template_name = "pages/clip.html"
    broadcaster_id = request.GET.get("broadcaster_id")
    first = request.GET.get("first")
    clips = get_clips(request, broadcaster_id, first)
    return render(request, template_name, {"clips": clips})


@login_required(login_url="/accounts/login/")
def your_clip_page(request):
    template_name = "pages/clip.html"
    user_token = get_token(request)
    user_game_follows_clips = get_user_game_follows_clips(request, user_token)
    user_channel_follows = get_user_follows2(request, user_token)
    clips = get_user_games_channels_clips(user_game_follows_clips, user_channel_follows)
    return render(request, template_name, {"clips": clips})


@api_view(["GET"])
def my_view(request):
    follows = get_user_follows(request)
    return Response(data=follows)


@api_view(["GET"])
def followed_games_clips(request):
    clips = get_user_game_follows_clips(request)
    return Response(data=clips)


@api_view(["GET"])
def chosen_clips(request):
    user_game_follows_clips = get_user_game_follows_clips(request)
    user_channel_follows = get_user_follows(request)
    clips = get_user_games_channels_clips(user_game_follows_clips, user_channel_follows)
    return Response(data=clips)


@api_view(["GET"])
def broadcaster_top_clips_view(request):
    clips = get_clips_of_specific_channel(26261471, request)
    return Response(data=clips)


@api_view(["GET"])
def my_test_view(request):
    token = get_token(request)
    return Response(data=token)


@api_view(["GET"])
def top_games_view(request):
    games = get_top_games(request)
    return Response(data=games)


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
    bulk_info = get_user_bulk_info(broadcasters_id, request)
    return Response(data=bulk_info)
