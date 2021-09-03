import environ
from django.contrib.auth import get_user_model
from future.backports.datetime import timedelta, timezone, datetime

from config import celery_app
from glip.games.models import Game
from glip.games.utils import get_and_save_games_clips

User = get_user_model()

env = environ.Env()


@celery_app.task()
def save_game_clips():
    time_threshold = datetime.now() - timedelta(minutes=5)
    not_updated_games = Game.objects.filter(last_queried_clips__lt=time_threshold)
    not_updated_games_ids = []
    for game in not_updated_games:
        not_updated_games_ids.append(game.game_id)
    if len(not_updated_games_ids) > 0:
        for game_id in not_updated_games_ids:
            get_and_save_games_clips(game_id)
