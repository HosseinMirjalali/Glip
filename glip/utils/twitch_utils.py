"""

A single file that includes all functions that are needed for communicating with Twitch API for fetching different types
of data.

"""
import environ
import requests
from allauth.socialaccount.models import SocialAccount, SocialToken

env = environ.Env()


class TwitchAPICallerBase(object):
    """
    A base class that defines common properties required by other Twitch API caller classes
    """

    # URLs used in calling Twitch API for different purposes
    VALIDATION_URL = "https://id.twitch.tv/oauth2/validate"
    FOLLOWS_URL = "https://api.twitch.tv/helix/users/follows?from_id=%s&first=100"
    FOLLOWS_URL_CURSOR = (
        "https://api.twitch.tv/helix/users/follows?after=%s&from_id=%s&first=100"
    )
    BROADCASTER_CLIP_URL = "https://api.twitch.tv/helix/users?id=%s"
    BROADCASTER_INFO_URL = "https://api.twitch.tv/helix/users?"
    LIVE_DATA_URL = "https://api.twitch.tv/helix/streams?"
    TOP_GAMES_URL = "https://api.twitch.tv/helix/games/top?first=%s"
    client_id = env("TWITCH_CLIENT_ID")

    def __init__(self, request):
        """
        Constructor. Includes all the instance variables and function objects
        """
        self.request = request
        self.account = SocialAccount.objects.get(user=request.user)
        self.social_token = SocialToken.objects.get(account=self.account)
        self.token = self.social_token.token
        self.headers = {
            "Authorization": "Bearer {}".format(self.token),
            "Client-ID": self.client_id,
        }
        self.user_twitch_id = SocialAccount.objects.get(user=self.request.user).uid


class TwitchAPICaller(TwitchAPICallerBase):
    """
    Main functions of calling Twitch API with the current method
    """

    def validate_token(self):
        """
        Validates user's token
        :return: Boolean
        """
        response_data = requests.get(self.VALIDATION_URL, headers=self.headers)
        if response_data.status_code == 401:
            return False
        return True

    def get_user_follows(self):
        """
        Gets user's followed streamers from Twitch API and returns a dictionary containing those
        :return:
        """

        follows = []
        self.FOLLOWS_URL = self.FOLLOWS_URL % self.user_twitch_id
        r = requests.get(self.FOLLOWS_URL, headers=self.headers)
        response_data = r.json()
        for data in response_data["data"]:
            follows.append(data)
        while "cursor" in response_data["pagination"]:
            cursor = response_data["pagination"]["cursor"]
            self.FOLLOWS_URL_CURSOR = self.FOLLOWS_URL_CURSOR % (
                cursor,
                self.user_twitch_id,
            )
            r = requests.get(self.FOLLOWS_URL_CURSOR, headers=self.headers)
            response_data = r.json()
            for data in response_data["data"]:
                follows.append(data)
        return follows
