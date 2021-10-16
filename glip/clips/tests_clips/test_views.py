import datetime
from unittest import TestCase

import pytest
from django.contrib.auth.models import AnonymousUser
from django.test import Client, RequestFactory

from glip.clips.models import Clip
from glip.clips.views import local_clip_detail_page
from glip.games.models import Game
from glip.users.models import User

pytestmark = pytest.mark.django_db


class TestClipDetailView(TestCase):
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
            created_at=datetime.datetime.now(),
            thumbnail_url="https://clips-media-assets2.twitch.tv/AT-cm%7CHSCQyY59sYdqFvjRu4CUHQ-preview-480x272.jpg",
            duration="17.3",
        )

    def test_anonymous(self):
        """
        Tests that anyone can access a clip detail page without authentication
        """
        request = self.factory.get("/clips/clip")
        view = local_clip_detail_page(request, pk=self.clip.clip_twitch_id)

        request.user = AnonymousUser()

        view.request = request

        assert view.status_code == 200

    def test_authenticated(self):
        """
        Tests that logged-in users can access a clip detail page
        """
        request = self.factory.get("/clips/clip")
        view = local_clip_detail_page(request, pk=self.clip.clip_twitch_id)

        request.user = self.user

        assert view.status_code == 200

    def test_wrong_clip_id(self):
        """
        Tests that providing a wrong id should result in 404
        """
        request = self.factory.get("/clips/clip")
        view = local_clip_detail_page(request, pk="ObviouslyWrongClipID")

        request.user = self.user

        assert view.status_code == 404
