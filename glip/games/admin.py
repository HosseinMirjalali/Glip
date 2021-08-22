from django.contrib import admin

from glip.games.models import Game, GameFollow


class GameAdmin(admin.ModelAdmin):
    pass


class GameFollowAdmin(admin.ModelAdmin):
    pass


admin.site.register(Game, GameAdmin)
admin.site.register(GameFollow, GameFollowAdmin)
