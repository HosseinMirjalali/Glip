from django.urls import path

from .views import follows_view, my_view

app_name = "clips"
urlpatterns = [
    path("followed", view=follows_view, name="followed"),
    path("api/followed", view=my_view, name="api-followed"),
]
