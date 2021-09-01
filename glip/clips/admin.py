from django.contrib import admin

from glip.clips.models import Clip


class ClipAdmin(admin.ModelAdmin):
    pass


admin.site.register(Clip, ClipAdmin)
