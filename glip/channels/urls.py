from django.urls import path

from .views import api_follows, clip_page, follows_view, local_broadcaster_clip_view

app_name = "channels"
urlpatterns = [
    path("followed", view=follows_view, name="followed"),
    path("follows", view=api_follows, name="follows"),
    path("clip/", view=clip_page, name="clip"),
    path("clips/", view=local_broadcaster_clip_view, name="localchannelclip"),
]
