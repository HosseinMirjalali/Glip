from unittest import TestCase, mock

import pytest
from allauth.socialaccount.models import SocialAccount, SocialApp, SocialToken
from django.test import Client, RequestFactory
from django.urls import reverse
from django.utils import timezone

from glip.clips.models import Clip, TopClip
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


def add_middleware_to_request(request, middleware_class):
    middleware = middleware_class()
    middleware.process_request(request)
    return request


def add_middleware_to_response(request, middleware_class):
    middleware = middleware_class()
    middleware.process_response(request)
    return request


class TestClipDetailView(TestCase):
    """
    Tests regarding Clips Detail page ( local_clip_detail_page )
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
    def test_anonymous(self):
        """
        Tests that anyone can access a clip detail page without authentication
        """

        url = reverse("clips:clip_detail", args=[self.clip.clip_twitch_id])
        response = self.c.get(url)
        assert response.status_code == 200
        assert response.context["clip"] == self.clip

    @pytest.mark.client
    def test_authenticated(self):
        """
        Tests that logged-in users can access a clip detail page
        """

        url = reverse("clips:clip_detail", args=[self.clip.clip_twitch_id])
        self.c.login(username="test", password="top_secret")
        response = self.c.get(url)
        assert response.status_code == 200
        assert response.context["clip"] == self.clip

    @pytest.mark.factory
    def test_wrong_clip_id(self):
        """
        Tests that providing a wrong id results in 404
        """
        request = self.factory.get("/clips/clip")
        request.user = self.user
        view = local_clip_detail_page(request, pk="ObviouslyWrongClipID")
        assert view.status_code == 404

    @pytest.mark.client
    def test_liked_clip_is_faved(self):
        """
        Test that a liked clip has a True fav
        :return:
        """
        url = reverse("clips:clip_detail", args=[self.clip.clip_twitch_id])
        self.c.login(username="test", password="top_secret")
        response = self.c.get(url)
        assert response.context["fav"]

    @pytest.mark.client
    def test_comment_is_shown(self):
        """
        Test that a clip that has a comment is shown in the page
        :return:
        """
        url = reverse("clips:clip_detail", args=[self.clip.clip_twitch_id])
        response = self.c.get(url)
        assert response.context["comments"][0] == self.comment


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
        self.game.follows.add(self.user)
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
    Tests regarding feed view ( feed_view )
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

    def context(self, call_args):
        args, kwargs = call_args
        request_mock, template, context = args
        return context

    @pytest.mark.client
    def test_no_users_authed(self):
        """
        Tests that homepage shows clips when user IS NOT logged in
        :return:
        """

        response = self.c.get(reverse("home"))
        assert response.status_code == 200
        assert len(response.context["clips"]) == 2

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
        assert len(response.context["clips"]) == 2

    @pytest.mark.client
    def test_comment_exists(self):
        """
        Tests that when a comment exists, the comment_count is correctly shown
        :return:
        """

        self.c.login(username="test", password="top_secret")
        response = self.c.get("/")
        assert response.status_code == 200
        assert response.context["clips"][0].comment_count == 1

    @pytest.mark.client
    def test_like_exists(self):
        """
        Tests that a liked clip has a 1 like count and a not-liked clip has 0
        :return:
        """
        url = reverse("clips:feed")
        self.c.login(username="test", password="top_secret")
        response = self.c.get(url)
        assert response.status_code == 200
        assert response.context["clips"][0].likes_count == 1
        assert response.context["clips"][0].fav
        assert response.context["clips"][0] == self.clip

    @pytest.mark.client
    def test_like_doesnt_exist(self):
        """
        Test that a not liked clip has 0 like count
        :return:
        """
        url = reverse("clips:feed")
        self.c.login(username="test", password="top_secret")
        response = self.c.get(url)
        assert response.status_code == 200
        assert response.context["clips"][1].likes_count == 0
        assert response.context["clips"][1].fav is False


class TestLikeClip(TestCase):
    """
    Tests regarding liking a clip (like_clip)
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
        # self.like = self.clip.likes.add(self.user)
        self.comment = Comment.objects.create(
            user=self.user,
            clip=self.clip,
            reply=None,
            content="Test123",
            timestamp=timezone.now(),
        )

    @pytest.mark.client
    def test_authed_user(self):
        """
        Test that an authenticated user can like a clip
        :return:
        """
        url = reverse("clips:like-clip")
        self.c.login(username="test", password="top_secret")
        response = self.c.post(
            url, data={"clip_id": self.clip.clip_twitch_id, "action": "post"}
        )
        assert response.status_code == 200
        assert self.clip.likes.filter(id=self.user.id).exists()

    @pytest.mark.client
    def test_no_auth_user(self):
        """
        Test that a non-authorized user can NOT like a clip
        :return:
        """
        url = reverse("clips:like-clip")
        response = self.c.post(
            url, data={"clip_id": self.clip.clip_twitch_id, "action": "post"}
        )
        assert response.status_code == 302
        assert self.clip.likes.count() == 0
