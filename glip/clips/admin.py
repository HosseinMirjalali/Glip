from django.contrib import admin

from glip.clips.models import Channels, Game


class ChannelsAdmin(admin.ModelAdmin):
    pass


class GameAdmin(admin.ModelAdmin):
    pass


admin.site.register(Channels, ChannelsAdmin)
admin.site.register(Game, GameAdmin)
