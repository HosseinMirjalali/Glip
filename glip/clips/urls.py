from django.urls import path

from .views import broadcaster_top_clips_view, clips_view, follows_view, my_view

app_name = "clips"
urlpatterns = [
    path("followed", view=follows_view, name="followed"),
    path("clips", view=clips_view, name="clips"),
    path("api/followed", view=my_view, name="api-followed"),
    path("api/clip", view=broadcaster_top_clips_view, name="api-clip"),
]
