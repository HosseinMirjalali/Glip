from django.urls import path

from .views import clip_page, follows_view

app_name = "channels"
urlpatterns = [
    path("followed", view=follows_view, name="followed"),
    path("clip/", view=clip_page, name="clip"),
]
