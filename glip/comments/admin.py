from django.contrib import admin

from glip.comments.models import Comment


class CommentAdmin(admin.ModelAdmin):
    pass
    # list_display = (
    #     "user",
    #     "clip",
    #     "content",
    #     "timestamp"
    # )
    # search_fields = ["user", "clip", "timestamp"]


admin.site.register(Comment, CommentAdmin)
