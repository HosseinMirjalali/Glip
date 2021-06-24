from django.contrib import admin

from glip.clips.models import Channels


class ChannelsAdmin(admin.ModelAdmin):
    pass


admin.site.register(Channels, ChannelsAdmin)
