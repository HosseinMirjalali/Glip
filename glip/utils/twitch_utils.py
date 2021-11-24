"""

A single file that includes all functions that are needed for communicating with Twitch API for fetching different types
of data.

"""
from allauth.socialaccount.models import SocialAccount, SocialToken


class TwitchAPICaller(object):
    """
    A base class that defines common properties required by other Twitch API caller classes
    """

    # URLs used in calling Twitch API for different purposes
    VALIDATION_URL = "https://id.twitch.tv/oauth2/validate"
    FOLLOWS_URL = "https://api.twitch.tv/helix/users/follows?from_id={}&first=100"
    BROADCASTER_CLIP_URL = "https://api.twitch.tv/helix/users?id={}"
    BROADCASTER_INFO_URL = "https://api.twitch.tv/helix/users?"
    LIVE_DATA_URL = "https://api.twitch.tv/helix/streams?"
    TOP_GAMES_URL = "https://api.twitch.tv/helix/games/top?first={}"

    def __init__(self, request):
        """
        Constructor. Includes all the instance variables and function objects
        """
        self.request = request
        self.token = SocialToken.objects.get(
            SocialAccount.objects.get(user=self.request.user)
        )
        self.headers = {"Authorization": "Bearer {}".format(self.token)}
