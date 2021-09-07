import environ
from django.contrib.auth import get_user_model
from future.backports.datetime import timedelta, timezone, datetime

from config import celery_app
from glip.games.models import Game
from glip.games.utils import get_and_save_games_clips
from contextlib import contextmanager
import time
from django.core.cache import cache
from hashlib import md5

User = get_user_model()

env = environ.Env()
time_threshold = datetime.now() - timedelta(minutes=5)

LOCK_EXPIRE = 60 * 10  # Lock expires in 10 minutes


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
    lock_id = '{0}-lock-{1}'.format(self.name, feed_url_hexdigest)
    with memcache_lock(lock_id, self.app.oid) as acquired:
        if acquired:
            not_updated_games = Game.objects.filter(last_queried_clips__lt=time_threshold)
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
