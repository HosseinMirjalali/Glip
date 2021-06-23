from django.urls import path

from .views import clips_view

app_name = "clips"
urlpatterns = [
    path("clips/followed", view=clips_view, name="clips"),
]
