from django.contrib import admin

from glip.games.models import Game, GameFollow


class GameAdmin(admin.ModelAdmin):
    list_display = ('game_id', 'name',)
    search_fields = ['game_id', 'name']


class GameFollowAdmin(admin.ModelAdmin):
    pass


admin.site.register(Game, GameAdmin)
admin.site.register(GameFollow, GameFollowAdmin)
