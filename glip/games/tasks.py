import time
from contextlib import contextmanager
from hashlib import md5

import environ
from django.contrib.auth import get_user_model
from django.core.cache import cache
from future.backports.datetime import datetime, timedelta

from config import celery_app
from glip.games.models import Game, TopGame
from glip.games.utils import get_all_top_games, get_and_save_games_clips

User = get_user_model()

env = environ.Env()
time_threshold = datetime.now() - timedelta(minutes=5)

LOCK_EXPIRE = 60 * 10  # Lock expires in 10 minutes


def past_x_hours(x):
    return datetime.now() - timedelta(hours=x)


def past_x_minutes(x):
    return datetime.now() - timedelta(minutes=x)


@contextmanager
def memcache_lock(lock_id, oid):
    timeout_at = time.monotonic() + LOCK_EXPIRE - 3
    # cache.add fails if the key already exists
    status = cache.add(lock_id, oid, LOCK_EXPIRE)
    try:
        yield status
    finally:
        # memcache delete is very slow, but we have to use it to take
        # advantage of using add() for atomic locking
        if time.monotonic() < timeout_at and status:
            # don't release the lock if we exceeded the timeout
            # to lessen the chance of releasing an expired lock
            # owned by someone else
            # also don't release the lock if we didn't acquire it
            cache.delete(lock_id)


@celery_app.task()
def save_game_clips():
    not_updated_games = Game.objects.filter(last_queried_clips__lt=time_threshold)
    not_updated_games_ids = []
    count = 0
    for game in not_updated_games:
        not_updated_games_ids.append(game.game_id)
    if len(not_updated_games_ids) > 0:
        for game_id in not_updated_games_ids:
            count += 1
            get_and_save_games_clips(game_id)
            if count >= 5:
                break
    return True


@celery_app.task(bind=True)
def save_clips_with_lock(self):
    # The cache key consists of the task name and the MD5 digest
    # of the feed URL.
    feed_url_hexdigest = md5().hexdigest()
    lock_id = "{0}-lock-{1}".format(self.name, feed_url_hexdigest)
    with memcache_lock(lock_id, self.app.oid) as acquired:
        if acquired:
            not_updated_games = Game.objects.filter(
                last_queried_clips__lt=time_threshold
            )
            not_updated_games_ids = []
            count = 0
            for game in not_updated_games:
                not_updated_games_ids.append(game.game_id)
            if len(not_updated_games_ids) > 0:
                for game_id in not_updated_games_ids:
                    count += 1
                    get_and_save_games_clips(game_id)
                    if count >= 10:
                        break
            return True


@celery_app.task()
def get_feed(past_x: int):
    # Game.objects.all().update(last_queried_clips=datetime.now() - timedelta(minutes=61))
    # Game.objects.all().update(last_tried_query=datetime.now() - timedelta(minutes=31))
    not_updated_games = (
        Game.objects.filter(last_queried_clips__lt=past_x_hours(past_x))
        .filter(last_tried_query__lt=past_x_minutes(30))
        .order_by("game_id")
    )
    top_games = TopGame.objects.all()
    top_games_ids = []
    for game in top_games:
        top_games_ids.append(game.id)

    not_updated_games_ids = []
    # count = 0
    print("!!!!!!!!!!!!!!!!!!!!!!!!")
    print(not_updated_games)
    for game in not_updated_games:
        not_updated_games_ids.append(game.game_id)
    if len(not_updated_games_ids) > 0:
        for game_id in not_updated_games_ids:
            if game_id in top_games_ids:
                get_and_save_games_clips(game_id)
                break
                # count += 1
                # if count >= 1:
                #     break
    return True


@celery_app.task()
def purge_other_tasks():
    celery_app.control.purge()


@celery_app.task()
def get_and_set_top_games():
    games = get_all_top_games()
    TopGame.objects.all().delete()
    order = 1
    objs = []
    for g in games:
        objs.append(
            TopGame(
                id=g["id"], name=g["name"], box_art_url=g["box_art_url"], order=order
            )
        )
        order += 1
    games_to_save = [
        Game(
            game_id=e["id"],
            name=e["name"],
            box_art_url=e["box_art_url"],
            last_queried_clips=datetime.now() - timedelta(minutes=61),
            last_tried_query=datetime.now() - timedelta(minutes=31),
        )
        for e in games
    ]
    Game.objects.bulk_create(games_to_save, ignore_conflicts=True)
    TopGame.objects.bulk_create(objs, ignore_conflicts=True)


@celery_app.task()
def get_feed_from_last(past_x: int):
    not_updated_games = (
        list(
            Game.objects.filter(last_queried_clips__lt=past_x_hours(past_x))
            .filter(last_tried_query__lt=past_x_minutes(30))
            .order_by("id")
        )
    )[:-1]
    not_updated_games_ids = []
    count = 0
    for game in not_updated_games:
        not_updated_games_ids.append(game.game_id)
    if len(not_updated_games_ids) > 0:
        for game_id in not_updated_games_ids:
            count += 1
            get_and_save_games_clips(game_id)
            if count >= 1:
                break
    return True
