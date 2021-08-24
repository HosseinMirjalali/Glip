from django.contrib import admin

from glip.channels.models import Channel


class ChannelAdmin(admin.ModelAdmin):
    pass


admin.site.register(Channel, ChannelAdmin)
