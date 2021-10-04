from django.contrib import admin

from glip.comments.models import Comment


class CommentAdmin(admin.ModelAdmin):
    list_display = ("user", "content", "timestamp")
    list_filter = ("user", "timestamp")
    search_fields = ["user", "timestamp"]
    raw_id_fields = ("clip", "reply")
    # readonly_fields = ("clip", "reply")


admin.site.register(Comment, CommentAdmin)
