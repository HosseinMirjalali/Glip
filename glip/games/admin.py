from django.contrib import admin

from glip.games.models import Game, GameFollow, TopGame


class GameAdmin(admin.ModelAdmin):
    list_display = ("game_id", "name", "last_queried_clips", "last_tried_query")
    search_fields = ["game_id", "name", "last_queried_clips", "last_tried_query"]


class GameFollowAdmin(admin.ModelAdmin):
    pass


class TopGameAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "name",
    )
    search_fields = ["id", "name"]


admin.site.register(Game, GameAdmin)
admin.site.register(GameFollow, GameFollowAdmin)
admin.site.register(TopGame, TopGameAdmin)
