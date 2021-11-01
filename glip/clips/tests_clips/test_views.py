from unittest import TestCase, mock

import pytest
from allauth.socialaccount.models import SocialAccount, SocialApp, SocialToken
from django.contrib.auth.models import AnonymousUser
from django.test import Client, RequestFactory
from django.urls import reverse
from django.utils import timezone

from glip.clips.models import Clip
from glip.clips.views import local_clip_detail_page
from glip.comments.models import Comment
from glip.games.models import Game, GameFollow
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


def mock_get_user_follows_empty(request, user_token):
    broadcaster = {}
    return broadcaster


def mock_get_user_follows_non_empty(request, user_token):
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


class TestClipDetailView(TestCase):
    """
    Tests regarding Clips Detail page ( local_clip_detail_page )
    """

    def setUp(self):
        self.factory = RequestFactory()
        self.client = Client
        self.user = User.objects.create_user(
            username="test", email="test@test.com", password="top_secret"
        )
        self.game = Game.objects.create(
            game_id="461067",
            name="Tekken 7",
            box_art_url="https://static-cdn.jtvnw.net/ttv-boxart/Tekken%207-{width}x{height}.jpg",
        )
        self.clip = Clip.objects.create(
            clip_twitch_id="ZealousVictoriousSamosaPlanking-jn2xh2oW-NG7gJQd",
            url="https://clips.twitch.tv/ZealousVictoriousSamosaPlanking-jn2xh2oW-NG7gJQd",
            embed_url="https://clips.twitch.tv/embed?clip=ZealousVictoriousSamosaPlanking-jn2xh2oW-NG7gJQd",
            broadcaster_id="425462523",
            broadcaster_name="Kenoq_",
            creator_id="230286742",
            creator_name="madara_irgen",
            video_id="1170882229",
            twitch_game_id="461067",
            game=self.game,
            language="nl",
            title="Chair get destroyed by angry fist that once destroyed closet ",
            twitch_view_count="9",
            glip_view_count="",
            created_at=timezone.now(),
            thumbnail_url="https://clips-media-assets2.twitch.tv/AT-cm%7CHSCQyY59sYdqFvjRu4CUHQ-preview-480x272.jpg",
            duration="17.3",
        )

    @pytest.mark.factory
    def test_anonymous(self):
        """
        Tests that anyone can access a clip detail page without authentication
        """
        request = self.factory.get("/clips/clip")
        view = local_clip_detail_page(request, pk=self.clip.clip_twitch_id)

        request.user = AnonymousUser()

        view.request = request

        assert view.status_code == 200

    @pytest.mark.factory
    def test_authenticated(self):
        """
        Tests that logged-in users can access a clip detail page
        """
        request = self.factory.get("/clips/clip")
        view = local_clip_detail_page(request, pk=self.clip.clip_twitch_id)

        request.user = self.user

        assert view.status_code == 200

    @pytest.mark.factory
    def test_wrong_clip_id(self):
        """
        Tests that providing a wrong id results in 404
        """
        request = self.factory.get("/clips/clip")
        view = local_clip_detail_page(request, pk="ObviouslyWrongClipID")

        request.user = self.user

        assert view.status_code == 404


class TestClipsForYou(TestCase):
    """
    Tests regarding ClipsForYou view ( new_your_clips_local )
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
            clip_twitch_id="ZealousVictoriousSamosaPlanking-jn2xh2oW-NG7gJQd",
            url="https://clips.twitch.tv/ZealousVictoriousSamosaPlanking-jn2xh2oW-NG7gJQd",
            embed_url="https://clips.twitch.tv/embed?clip=ZealousVictoriousSamosaPlanking-jn2xh2oW-NG7gJQd",
            broadcaster_id="425462523",
            broadcaster_name="Kenoq_",
            creator_id="230286742",
            creator_name="madara_irgen",
            video_id="1170882229",
            twitch_game_id="461067",
            game=self.game,
            language="nl",
            title="Chair get destroyed by angry fist that once destroyed closet ",
            twitch_view_count="9",
            glip_view_count="",
            created_at=timezone.now(),
            thumbnail_url="https://clips-media-assets2.twitch.tv/AT-cm%7CHSCQyY59sYdqFvjRu4CUHQ-preview-480x272.jpg",
            duration="17.3",
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

    @pytest.mark.client
    @mock.patch("glip.clips.views.validate_token", mock_validate_token)
    @mock.patch(
        "glip.clips.views.get_new_access_from_refresh", mock_get_new_access_from_refresh
    )
    @mock.patch("glip.clips.views.get_user_follows2", mock_get_user_follows_empty)
    def test_no_users_no_games_followed(self, *args, **kwargs):
        """
        Tests that view returns no clips when no broadcasters and no games are followed
        :param args: Mock Patches
        :param kwargs: Mock Patches
        :return: None
        """
        self.c.login(username="test", password="top_secret")
        response = self.c.get(reverse("clips:new_your_clips"))
        assert response.status_code == 200
        assert len(response.context["clips"]) == 0

    @pytest.mark.client
    @mock.patch("glip.clips.views.validate_token", mock_validate_token)
    @mock.patch(
        "glip.clips.views.get_new_access_from_refresh", mock_get_new_access_from_refresh
    )
    @mock.patch("glip.clips.views.get_user_follows2", mock_get_user_follows_non_empty)
    def test_users_followed_no_games_followed(self, *args, **kwargs):
        self.c.login(username="test", password="top_secret")
        response = self.c.get(reverse("clips:new_your_clips"))
        assert response.status_code == 200
        assert len(response.context["clips"]) == 0

    @pytest.mark.client
    @mock.patch("glip.clips.views.validate_token", mock_validate_token)
    @mock.patch(
        "glip.clips.views.get_new_access_from_refresh", mock_get_new_access_from_refresh
    )
    @mock.patch("glip.clips.views.get_user_follows2", mock_get_user_follows_non_empty)
    def test_users_and_game_followed(self, *args, **kwargs):
        """
        Tests that view returns a clip when user has followed broadcasters and games
        :param args: Mock Patches
        :param kwargs: Mock Patches
        :return: None
        """
        GameFollow.objects.create(
            following=self.user, followed=self.game, follow_time=timezone.now()
        )
        self.c.login(username="test", password="top_secret")
        response = self.c.get(reverse("clips:new_your_clips"))
        assert response.status_code == 200
        assert len(response.context["clips"]) == 1

    @pytest.mark.client
    @mock.patch("glip.clips.views.validate_token", mock_validate_token)
    @mock.patch(
        "glip.clips.views.get_new_access_from_refresh", mock_get_new_access_from_refresh
    )
    @mock.patch("glip.clips.views.get_user_follows2", mock_get_user_follows_empty)
    def test_game_followed_but_no_user(self, *args, **kwargs):
        """
        Test that view returns no clips when a game is followed but no broadcaster is followed
        :param args: Mock Patches
        :param kwargs: Mock Patches
        :return: None
        """
        GameFollow.objects.create(
            following=self.user, followed=self.game, follow_time=timezone.now()
        )
        self.c.login(username="test", password="top_secret")
        response = self.c.get(reverse("clips:new_your_clips"))
        assert response.status_code == 200
        assert len(response.context["clips"]) == 0


class TestFeedView(TestCase):
    """
    Tests regarding ClipsForYou view ( feed_view )
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
            clip_twitch_id="ZealousVictoriousSamosaPlanking-jn2xh2oW-NG7gJQd",
            url="https://clips.twitch.tv/ZealousVictoriousSamosaPlanking-jn2xh2oW-NG7gJQd",
            embed_url="https://clips.twitch.tv/embed?clip=ZealousVictoriousSamosaPlanking-jn2xh2oW-NG7gJQd",
            broadcaster_id="425462523",
            broadcaster_name="Kenoq_",
            creator_id="230286742",
            creator_name="madara_irgen",
            video_id="1170882229",
            twitch_game_id="461067",
            game=self.game,
            language="nl",
            title="Chair get destroyed by angry fist that once destroyed closet ",
            twitch_view_count="9",
            glip_view_count="",
            created_at=timezone.now(),
            thumbnail_url="https://clips-media-assets2.twitch.tv/AT-cm%7CHSCQyY59sYdqFvjRu4CUHQ-preview-480x272.jpg",
            duration="17.3",
        )
        self.clip_old = Clip.objects.create(
            clip_twitch_id="2ZealousVictoriousSamosaPlanking-jn2xh2oW-NG7gJQd",
            url="https://clips.twitch.tv/ZealousVictoriousSamosaPlanking-jn2xh2oW-NG7gJQd",
            embed_url="https://clips.twitch.tv/embed?clip=ZealousVictoriousSamosaPlanking-jn2xh2oW-NG7gJQd",
            broadcaster_id="425462523",
            broadcaster_name="Kenoq_",
            creator_id="230286742",
            creator_name="madara_irgen",
            video_id="1170882229",
            twitch_game_id="461067",
            game=self.game,
            language="nl",
            title="Chair get destroyed by angry fist that once destroyed closet ",
            twitch_view_count="9",
            glip_view_count="",
            created_at=timezone.now() - timezone.timedelta(weeks=2),
            thumbnail_url="https://clips-media-assets2.twitch.tv/AT-cm%7CHSCQyY59sYdqFvjRu4CUHQ-preview-480x272.jpg",
            duration="17.3",
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

    @pytest.mark.client
    def test_no_users_authed(self):
        """
        Tests that homepage shows clips when user IS NOT logged in
        :return:
        """

        response = self.c.get(reverse("home"))
        assert response.status_code == 200
        assert len(response.context["clips"]) == 1

    @pytest.mark.client
    def test_a_user_authed(self):
        """
        Tests that homepage shows clips when user IS logged in
        P.S. it also tests that old clip (self.clip_old) is not shown since it's from 2 weeks ago
        :return:
        """

        self.c.login(username="test", password="top_secret")
        response = self.c.get(reverse("home"))
        assert response.status_code == 200
        clips = response.context["clips"]
        assert clips[0].created_at < timezone.now()
        assert len(response.context["clips"]) == 1

    @pytest.mark.client
    def test_comment_exists(self):
        """
        Tests that when a comment exists, the comment_count is correctly shown
        :return:
        """

        Comment.objects.create(
            user=self.user,
            clip=self.clip,
            reply=None,
            content="Test123",
            timestamp=timezone.now(),
        )
        self.c.login(username="test", password="top_secret")
        response = self.c.get(reverse("home"))
        assert response.status_code == 200
        assert response.context["clips"][0].comment_count == 1
