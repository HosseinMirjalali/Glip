from django.contrib import admin

from glip.clips.models import Clip, TopClip


class ClipAdmin(admin.ModelAdmin):
    list_display = (
        "game",
        "clip_twitch_id",
        "title",
    )
    search_fields = ["game__name", "twitch_game_id", "clip_twitch_id"]


class TopClipAdmin(admin.ModelAdmin):
    pass


admin.site.register(Clip, ClipAdmin)
admin.site.register(TopClip, TopClipAdmin)
