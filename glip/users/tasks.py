import environ
from django.contrib.auth import get_user_model

from config import celery_app
from glip.channels.models import Channel
from glip.users.utils import get_user_follows

User = get_user_model()

env = environ.Env()


@celery_app.task()
def get_users_count():
    """A pointless Celery task to demonstrate usage."""
    return User.objects.count()


@celery_app.task()
def save_user_followers(request):
    follows = get_user_follows(request)
    user = User.objects.get(username=request.user.username)
    for i in follows:
        user.follows = i["to_id"]
        c = Channel(
            twitch_id=i["to_id"],
            twitch_login=i["to_login"],
            twitch_name=i["to_name"],
        )
        c.save()
        user.channels.add(c)
