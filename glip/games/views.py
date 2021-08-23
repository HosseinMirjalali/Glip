from datetime import datetime, timedelta

import environ
from allauth.socialaccount.models import SocialApp
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect, render
from django.urls import reverse
from django.views import View

from glip.games.models import Game, GameFollow
from glip.users.utils import get_clips_by_game, get_token, get_top_games

env = environ.Env()

User = get_user_model()

past_day = datetime.now() - timedelta(days=1)
formatted_past_day = past_day.isoformat()[:-3] + "Z"
client_id = SocialApp.objects.get(provider__iexact="twitch").client_id


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
            game["box_art_url"] = game["box_art_url"].replace("{width}", "285")
            game["box_art_url"] = game["box_art_url"].replace("{height}", "380")
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


@login_required(login_url="/accounts/login/")
def follow_game(request):
    game_id = request.GET.get("game_id")
    game_to_follow = Game.objects.get(game_id=game_id)
    user = request.user
    GameFollow.objects.get_or_create(following=user, followed=game_to_follow)
    return redirect(reverse("clips:games"))


@login_required(login_url="/accounts/login/")
def unfollow_game(request):
    game_id = request.GET.get("game_id")
    game_to_follow = Game.objects.get(game_id=game_id)
    user = request.user
    obj = GameFollow.objects.get(following=user, followed=game_to_follow)
    print("@@@@@@@@@@@@@@@@@@@@@@@@@@@")
    print(obj)
    obj.delete()
    return redirect(reverse("clips:games"))


@login_required(login_url="/accounts/login/")
def game_clip_page(request):
    template_name = "pages/clip.html"
    game_id = request.GET.get("game_id")
    # first = request.GET.get("first")
    user_token = get_token(request)
    clips = get_clips_by_game(request, game_id, user_token=user_token)
    print(clips)
    return render(request, template_name, {"clips": clips})
