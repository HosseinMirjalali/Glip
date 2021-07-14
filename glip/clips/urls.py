from django.urls import path

from .views import (
    broadcasters_info,
    clip_page,
    clips_view,
    follow_game,
    follows_view,
    game_top_clips_view,
    games_view,
    my_test_view,
    my_view,
    top_games_view,
)

app_name = "clips"
urlpatterns = [
    path("followed", view=follows_view, name="followed"),
    # re_path(r'^follow/(?P<game_id>[\d]+)/$', follow_game, name="follow_game"),
    path("follow_game/<str:game_id>", view=follow_game, name="follow_game"),
    path("games", view=games_view, name="games"),
    path("clips", view=clips_view, name="clips"),
    path("clip/", view=clip_page, name="clip"),
    path("api/followed", view=my_view, name="api-followed"),
    path("api/test", view=my_test_view, name="api-test"),
    path("api/games", view=top_games_view, name="api-games"),
    path("api/bulk", view=broadcasters_info, name="api-bulk-info"),
    path("gameclips", view=game_top_clips_view, name="game-clips"),
]
