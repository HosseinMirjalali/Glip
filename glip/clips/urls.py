from django.urls import path

from .views import (
    broadcasters_info,
    chosen_clips,
    clip_page,
    clips_view,
    follow_game,
    followed_games_clips,
    follows_view,
    futures_followed_clips,
    game_clip_page,
    game_top_clips_view,
    games_view,
    my_test_view,
    my_view,
    top_games_view,
    unfollow_game,
    your_clip_page,
)

app_name = "clips"
urlpatterns = [
    path("followed", view=follows_view, name="followed"),
    # re_path(r'^follow/(?P<game_id>[\d]+)/$', follow_game, name="follow_game"),
    path("follow_game", view=follow_game, name="follow_game"),
    path("unfollow_game", view=unfollow_game, name="unfollow_game"),
    path("games", view=games_view, name="games"),
    path("clips", view=clips_view, name="clips"),
    path("future", view=futures_followed_clips, name="future"),
    path("clip/", view=clip_page, name="clip"),
    path("gameclip/", view=game_clip_page, name="gameclip"),
    path("yourclips/", view=your_clip_page, name="your_clips"),
    path("api/followed", view=my_view, name="api-followed"),
    path("api/gameclips", view=followed_games_clips, name="api-gameclips"),
    path("api/chosen", view=chosen_clips, name="api-chosen"),
    path("api/test", view=my_test_view, name="api-test"),
    path("api/games", view=top_games_view, name="api-games"),
    path("api/bulk", view=broadcasters_info, name="api-bulk-info"),
    path("gameclips", view=game_top_clips_view, name="game-clips"),
]
