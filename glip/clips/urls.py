from django.urls import path

from .views import clips_view, my_view

app_name = "clips"
urlpatterns = [
    path("follow", view=clips_view, name="clips"),
    path("followed", view=my_view, name="followed"),
]
