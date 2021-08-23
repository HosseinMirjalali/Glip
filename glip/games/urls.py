from django.urls import path

from .views import follow_game, game_clip_page, games_view, unfollow_game

app_name = "games"
urlpatterns = [
    path("games", view=games_view, name="games"),
    path("follow_game", view=follow_game, name="follow_game"),
    path("unfollow_game", view=unfollow_game, name="unfollow_game"),
    path("gameclip/", view=game_clip_page, name="gameclip"),
]
