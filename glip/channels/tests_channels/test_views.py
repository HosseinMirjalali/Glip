from unittest import TestCase, mock

import pytest
from allauth.socialaccount.models import SocialAccount, SocialApp, SocialToken
from django.test import Client, RequestFactory
from django.urls import reverse
from django.utils import timezone

from glip.clips.models import Clip, TopClip
from glip.comments.models import Comment
from glip.games.models import Game
from glip.users.models import User

pytestmark = pytest.mark.django_db


def mock_get_user_follows_one_broadcaster(**kwargs):
    broadcaster = {
        "from_id": "171003792",
        "from_login": "iiisutha067iii",
        "from_name": "IIIsutha067III",
        "to_id": "23161357",
        "to_name": "LIRIK",
        "followed_at": "2017-08-22T22:55:24Z",
    }
    return broadcaster


def mock_get_user_follows_empty(request):
    broadcaster = {}
    return broadcaster


def mock_get_user_follows_non_empty(request):
    broadcaster = [
        {
            "from_id": "171003792",
            "from_login": "iiisutha067iii",
            "from_name": "IIIsutha067III",
            "to_id": "425462523",
            "to_name": "madara_irgen",
            "followed_at": "2017-08-22T22:55:24Z",
        }
    ]
    return broadcaster


def mock_get_user_bulk_info(first_100, request):
    broadcaster = [
        {
            "from_id": "171003792",
            "from_login": "iiisutha067iii",
            "from_name": "IIIsutha067III",
            "to_id": "425462523",
            "to_name": "madara_irgen",
            "followed_at": "2017-08-22T22:55:24Z",
        }
    ]
    return broadcaster


def mock_validate_token(token):
    return True


def mock_get_new_access_from_refresh(request):
    return True


def add_middleware_to_request(request, middleware_class):
    middleware = middleware_class()
    middleware.process_request(request)
    return request


def add_middleware_to_response(request, middleware_class):
    middleware = middleware_class()
    middleware.process_response(request)
    return request


class TestFollowsListView(TestCase):
    """
    Tests regarding follows list view (FollowsListView)
    """

    def setUp(self):
        self.factory = RequestFactory()
        self.c = Client()
        self.user = User.objects.create_user(username="test", email="test@test.com")
        self.user.set_password("top_secret")
        self.user.save()
        self.game = Game.objects.create(
            game_id="461067",
            name="Tekken 7",
            box_art_url="https://static-cdn.jtvnw.net/ttv-boxart/Tekken%207-{width}x{height}.jpg",
        )
        self.clip = Clip.objects.create(
            clip_twitch_id="ZealousVictoriousSamosaPlanking",
            url="https://clips.twitch.tv/ZealousVictoriousSamosaPlanking",
            embed_url="https://clips.twitch.tv/embed?clip=ZealousVictoriousSamosaPlanking",
            broadcaster_id="4254625231",
            broadcaster_name="Kenoq_1",
            creator_id="2302867421",
            creator_name="madara_irgen1",
            video_id="11708822291",
            twitch_game_id="4610671",
            game=self.game,
            language="nl",
            title="Chair get destroyed by angry fist that once destroyed closet1",
            twitch_view_count="9",
            glip_view_count="",
            created_at=timezone.now() - timezone.timedelta(hours=2),
            thumbnail_url="https://clips-media-assets2.twitch.tv/AT-cm%7CHSCQyY59sYdqFvjRu4CUHQ-preview-480x272.jpg",
            duration="17.3",
            like_count=0,
            disabled=False,
        )
        self.clip_other = Clip.objects.create(
            clip_twitch_id="ZealousVictoriousSamosaPlanking2",
            url="https://clips.twitch.tv/ZealousVictoriousSamosaPlanking2",
            embed_url="https://clips.twitch.tv/embed?clip=ZealousVictoriousSamosaPlanking2",
            broadcaster_id="42546252312",
            broadcaster_name="Kenoq_12",
            creator_id="23028674212",
            creator_name="madara_irgen12",
            video_id="117088222912",
            twitch_game_id="46106712",
            game=self.game,
            language="nl",
            title="Chair get destroyed by angry fist that once destroyed closet12",
            twitch_view_count="9",
            glip_view_count="",
            created_at=timezone.now() - timezone.timedelta(hours=2),
            thumbnail_url="https://clips-media-assets2.twitch.tv/AT-cm%7CHSCQyY59sYdqFvjRu4CUHQ-preview-480x272.jpg",
            duration="17.3",
            like_count=0,
            disabled=False,
        )
        self.clip_old = Clip.objects.create(
            clip_twitch_id="jn2xh2oW",
            url="https://clips.twitch.tv/jn2xh2oW",
            embed_url="https://clips.twitch.tv/embed?clip=jn2xh2oW",
            broadcaster_id="425462522",
            broadcaster_name="Kenoq__",
            creator_id="2302867422",
            creator_name="madara_irgenn",
            video_id="11708822299",
            twitch_game_id="4610677",
            game=self.game,
            language="nl",
            title="Chair get destroyed by angry fist that once destroyed closet ",
            twitch_view_count="8",
            glip_view_count="",
            created_at=timezone.now() - timezone.timedelta(weeks=2),
            thumbnail_url="https://clips-media-assets2.twitch.tv/AT-cm%7CHSCQyY59sYdqFvjRu4CUHQ-preview-480x272.jpg",
            duration="17.3",
            like_count=0,
            disabled=False,
        )
        self.social_account = SocialAccount.objects.create(
            user=self.user, provider="twitch"
        )
        self.social_app = SocialApp.objects.create(
            provider="twitch", name="twitch", client_id="client_id1234", secret="key264"
        )
        self.social_token = SocialToken.objects.create(
            app=self.social_app, account=self.social_account, token="2323token"
        )
        self.top_clip = TopClip.objects.create(clip=self.clip)
        self.top_clip_other = TopClip.objects.create(clip=self.clip_other)
        self.top_clip_old = TopClip.objects.create(clip=self.clip_old)
        self.like = self.clip.likes.add(self.user)
        self.comment = Comment.objects.create(
            user=self.user,
            clip=self.clip,
            reply=None,
            content="Test123",
            timestamp=timezone.now(),
        )

    @pytest.mark.client
    @mock.patch("glip.channels.views.get_user_follows", mock_get_user_follows_non_empty)
    @mock.patch("glip.channels.views.get_user_bulk_info", mock_get_user_bulk_info)
    def test_authed_users_followed(self):
        """
        Test that an authorized user gets list of followed users (that exist) from Twitch API
        :return:
        """
        url = reverse("channels:followed")
        self.c.login(username="test", password="top_secret")
        response = self.c.get(url)
        assert response.status_code == 200
        assert len(response.context["follows"]) == 1
        assert response.context["follows"][0]["to_id"] == "425462523"

    @pytest.mark.client
    @mock.patch("glip.channels.views.get_user_follows", mock_get_user_follows_empty)
    @mock.patch("glip.channels.views.get_user_bulk_info", mock_get_user_bulk_info)
    def test_authed_users_no_follows(self):
        """
        Test that an authorized user gets an empty list of followed users
        :return:
        """
        url = reverse("channels:followed")
        self.c.login(username="test", password="top_secret")
        response = self.c.get(url)
        assert response.status_code == 200
        assert len(response.context["follows"]) == 0
