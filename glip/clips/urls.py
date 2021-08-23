from django.urls import path

from .views import clips_view, futures_followed_clips, your_clip_page

app_name = "clips"
urlpatterns = [
    # re_path(r'^follow/(?P<game_id>[\d]+)/$', follow_game, name="follow_game"),
    path("clips", view=clips_view, name="clips"),
    path("future", view=futures_followed_clips, name="future"),
    path("yourclips/", view=your_clip_page, name="your_clips"),
]
