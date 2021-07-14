from django.contrib import admin

from glip.clips.models import Channels, Game, GameFollow


class ChannelsAdmin(admin.ModelAdmin):
    pass


class GameAdmin(admin.ModelAdmin):
    pass


class GameFollowAdmin(admin.ModelAdmin):
    pass


admin.site.register(Channels, ChannelsAdmin)
admin.site.register(Game, GameAdmin)
admin.site.register(GameFollow, GameFollowAdmin)
