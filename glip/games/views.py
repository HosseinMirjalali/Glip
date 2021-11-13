from datetime import datetime, timedelta

import environ
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Count, Exists, OuterRef
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, render
from django.views import View

from glip.clips.models import Clip
from glip.games.models import Game, GameFollow, TopGame
from glip.users.utils import get_clips_by_game, get_token

env = environ.Env()

User = get_user_model()

past_day = datetime.now() - timedelta(days=1)
formatted_past_day = past_day.isoformat()[:-3] + "Z"
client_id = env("TWITCH_CLIENT_ID")


class GamesListView(LoginRequiredMixin, View):
    template_name = "pages/games.html"
    context_object_name = "games"

    def get(self, request):
        """
        Gets list of top 200 games on twitch
        """
        template_name = "pages/games.html"
        games = (
            TopGame.objects.all()
            .values()
            .annotate(
                followed=Exists(
                    User.objects.filter(
                        follow__game_id=OuterRef("pk"), id=request.user.id
                    )
                )
            )
        )
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


# @login_required(login_url="/accounts/login/")
# def follow_game(request):
#     game_id = request.GET.get("game_id")
#     game_to_follow = Game.objects.get(game_id=game_id)
#     user = request.user
#     GameFollow.objects.get_or_create(following=user, followed=game_to_follow)
#     return redirect(reverse("games:games"))
#
#
# @login_required(login_url="/accounts/login/")
# def unfollow_game(request):
#     game_id = request.GET.get("game_id")
#     game_to_follow = Game.objects.get(game_id=game_id)
#     user = request.user
#     obj = GameFollow.objects.get(following=user, followed=game_to_follow)
#     print("@@@@@@@@@@@@@@@@@@@@@@@@@@@")
#     print(obj)
#     obj.delete()
#     return redirect(reverse("games:games"))


@login_required
def follow_game(request):
    if request.POST.get("action") == "post":
        result = ""
        game_id = request.POST.get("clip_id")
        game = get_object_or_404(Game, game_id=game_id)
        print("@@@@@@@@@@@@@@@@@@@@@@@@@")
        print(game)
        print(game.follows.all())
        if game.follows.filter(id=request.user.id).exists():
            game.follows.remove(request.user)
            result = game.follows.all().count()
            game.save()
        else:
            game.follows.add(request.user)
            result = game.follows.all().count()
            game.save()

        return JsonResponse({"result": result})


@login_required(login_url="/accounts/login/")
def game_clip_page(request):
    template_name = "pages/clip.html"
    game_name = request.GET.get("name")
    if game_name:
        template_info = "Top clips of %s from the past 24 hours" % game_name
    else:
        template_info = "Top clips of the Twitch streamer you selected"
    game_id = request.GET.get("game_id")
    user_token = get_token(request)
    clips = get_clips_by_game(request, game_id, user_token=user_token)
    context = {"clips": clips, "template_info": template_info}
    return render(request, template_name, context)


class NoAuthGamesListView(View):
    context_object_name = "noauthgames"

    def get(self, request):
        template_name = "pages/new_games.html"
        games = TopGame.objects.all().values()
        games_dict = {"games": games}
        for game in games:
            game["box_art_url"] = game["box_art_url"].replace("{width}", "285")
            game["box_art_url"] = game["box_art_url"].replace("{height}", "380")
        return render(request, template_name, context=games_dict)


noauthgameslist = NoAuthGamesListView.as_view()


def local_game_clip_view(request):
    template_name = "pages/clips_no_modal_page.html"
    game_name = request.GET.get("name")
    template_info = f"Top {game_name} Twitch clips"
    start = datetime.now() - timedelta(hours=24)
    end = datetime.now()
    clips = (
        Clip.objects.filter(game__name=game_name)
        .filter(created_at__range=[start, end])
        .exclude(disabled=True)
        .order_by("-twitch_view_count")[:100]
    )
    context = {"clips": clips, "template_info": template_info}

    return render(request, template_name, context)


def local_game_clip_view_new(request, pk):
    template_name = "pages/new_clip.html"
    # game_name = request.GET.get("name")
    game_name = Game.objects.get(game_id=pk).name
    template_info = f"Top {game_name} Twitch clips"
    start = datetime.now() - timedelta(hours=24)
    end = datetime.now()
    clips = (
        Clip.objects.filter(game__game_id=pk)
        .filter(created_at__range=[start, end])
        .exclude(disabled=True)
        .annotate(
            fav=Exists(User.objects.filter(like=OuterRef("pk"), id=request.user.id))
        )
        .annotate(comment_count=Count("comments"))
        .annotate(likes_count=Count("likes"))
        .order_by("-twitch_view_count")[:100]
    )
    context = {"clips": clips, "template_info": template_info}

    return render(request, template_name, context)
