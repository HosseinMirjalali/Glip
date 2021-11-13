from django.urls import path

from .views import (  # unfollow_game,
    follow_game,
    game_clip_page,
    games_view,
    local_game_clip_view,
    local_game_clip_view_new,
    noauthgameslist,
)

app_name = "games"
urlpatterns = [
    path("", view=games_view, name="games"),
    path("topgames", view=noauthgameslist, name="topgames"),
    path("follow/", view=follow_game, name="follow_game"),
    # path("unfollow_game", view=unfollow_game, name="unfollow_game"),
    path("gameclip/", view=game_clip_page, name="gameclip"),
    path("clips/", view=local_game_clip_view, name="localgameclip"),
    path("topclips/<pk>", view=local_game_clip_view_new, name="localgameclipnew"),
]
