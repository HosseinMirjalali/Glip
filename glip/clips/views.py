from django.contrib.auth import get_user_model
from django.http import HttpResponse
from django.views import View

from glip.clips.utils import get_clips, get_user_twitch_id

User = get_user_model()


class ClipListView(View):
    template_name = "pages/clipslist.html"
    context_object_name = "clips"

    # def get_context_data(self, **kwargs):
    #     twitch_id = self.get_user_twitch_id(self.request)
    #     clips = get_clips(twitch_id)
    #     return HttpResponse(clips)
    #
    def get(self, request):
        twitch_id = get_user_twitch_id(request)
        clips = get_clips(twitch_id)
        return HttpResponse(clips)


clips_view = ClipListView.as_view()
