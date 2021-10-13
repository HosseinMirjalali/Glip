from django.urls import path

from .views import (
    ClipsJsonListView,
    clips_view,
    feed_view,
    futures_followed_clips,
    like_clip,
    local_clip_detail_page,
    new_your_clips_local,
    your_clip_page,
)

app_name = "clips"
urlpatterns = [
    # re_path(r'^follow/(?P<game_id>[\d]+)/$', follow_game, name="follow_game"),
    path("clips", view=clips_view, name="clips"),
    path("clip/<pk>", view=local_clip_detail_page, name="clip_detail"),
    path("clip_json", view=ClipsJsonListView.as_view(), name="clips-json"),
    path("future", view=futures_followed_clips, name="future"),
    path("feed", view=feed_view, name="feed"),
    path("yourclips/", view=your_clip_page, name="your_clips"),
    path("clipsforyou/", view=new_your_clips_local, name="new_your_clips"),
    path("like/", view=like_clip, name="like-clip"),
]
