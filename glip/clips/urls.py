from django.urls import path

from .views import (
    broadcasters_info,
    chosen_clips,
    clip_page,
    clips_view,
    follow_game,
    followed_games_clips,
    follows_view,
    game_top_clips_view,
    games_view,
    my_test_view,
    my_view,
    top_games_view,
    your_clip_page,
)

app_name = "clips"
urlpatterns = [
    path("followed", view=follows_view, name="followed"),
    # re_path(r'^follow/(?P<game_id>[\d]+)/$', follow_game, name="follow_game"),
    path("follow_game/<str:game_id>", view=follow_game, name="follow_game"),
    path("games", view=games_view, name="games"),
    path("clips", view=clips_view, name="clips"),
    path("clip/", view=clip_page, name="clip"),
    path("yourclips/", view=your_clip_page, name="your_clips"),
    path("api/followed", view=my_view, name="api-followed"),
    path("api/gameclips", view=followed_games_clips, name="api-gameclips"),
    path("api/chosen", view=chosen_clips, name="api-chosen"),
    path("api/test", view=my_test_view, name="api-test"),
    path("api/games", view=top_games_view, name="api-games"),
    path("api/bulk", view=broadcasters_info, name="api-bulk-info"),
    path("gameclips", view=game_top_clips_view, name="game-clips"),
]
