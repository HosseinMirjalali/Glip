from django.urls import path

from .views import (
    broadcaster_top_clips_view,
    broadcasters_info,
    clip_page,
    clips_view,
    follows_view,
    game_top_clips_view,
    my_view,
)

app_name = "clips"
urlpatterns = [
    path("followed", view=follows_view, name="followed"),
    path("clips", view=clips_view, name="clips"),
    path("clip/", view=clip_page, name="clip"),
    path("api/followed", view=my_view, name="api-followed"),
    path("api/clip", view=broadcaster_top_clips_view, name="api-clip"),
    path("api/bulk", view=broadcasters_info, name="api-bulk-info"),
    path("gameclips", view=game_top_clips_view, name="game-clips"),
]
