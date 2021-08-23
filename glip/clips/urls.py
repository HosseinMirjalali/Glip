from django.urls import path

from .views import (
    clips_view,
    follow_game,
    futures_followed_clips,
    game_clip_page,
    games_view,
    unfollow_game,
    your_clip_page,
)

app_name = "clips"
urlpatterns = [
    # re_path(r'^follow/(?P<game_id>[\d]+)/$', follow_game, name="follow_game"),
    path("follow_game", view=follow_game, name="follow_game"),
    path("unfollow_game", view=unfollow_game, name="unfollow_game"),
    path("games", view=games_view, name="games"),
    path("clips", view=clips_view, name="clips"),
    path("future", view=futures_followed_clips, name="future"),
    path("gameclip/", view=game_clip_page, name="gameclip"),
    path("yourclips/", view=your_clip_page, name="your_clips"),
]
