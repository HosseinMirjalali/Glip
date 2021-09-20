from django.contrib import admin

from glip.clips.models import Clip


class ClipAdmin(admin.ModelAdmin):
    list_display = (
        "game",
        "clip_twitch_id",
        "title",
    )
    search_fields = ["game__name", "twitch_game_id"]


admin.site.register(Clip, ClipAdmin)
