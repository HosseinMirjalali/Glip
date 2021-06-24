from django.urls import path

from .views import follows_view, my_view

app_name = "clips"
urlpatterns = [
    path("follow", view=follows_view, name="clips"),
    path("followed", view=my_view, name="followed"),
]
