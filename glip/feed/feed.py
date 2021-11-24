"""
Simple and first iteration of smart feed "algorithm" that makes "clips for you" view a little bit smart(er)

It takes into account more than just whether the user has followed the streamer or not.

For starters, there will be a custom scoring function that takes into account view count of the clip, view count of the
clip on Glip (which is currently not implemented to increment on views), game's average view count, the streamer's
average view count and/or sub/follow count.

"""
from typing import List


class FeedBase:
    """
    The main class that provides useful methods, properties that can be used
    for types of Feed algorithms/processes.
    """

    # def __init__(self, **kwargs):
    #     """
    #     Constructor. Can contain helpful extra keyword arguments, and other things.
    #     """
    #     # Go through keyword arguments, and either save their values to our
    #     # instance, or raise an error.
    #     for key, value in kwargs.items():
    #         setattr(self, key, value)

    def __init__(self):
        """
        Constructor.
        """
        self.clips: List[str] = []
        self.broadcaster_follows: List[str] = []
        self.game_follows: List[str] = []
        self.sorted_clips = self.__clips_sorted_by_view(self.clips)

    def clips_sorted_by_view(self, clips):
        return sorted(clips)

    __clips_sorted_by_view = clips_sorted_by_view


class FeedByScore(FeedBase):
    """
    Spits out clips by a scoring system
    """
