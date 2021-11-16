from django.urls import path

from .views import like_comment

app_name = "comments"

urlpatterns = [
    path("like/", view=like_comment, name="like-comment"),
]
