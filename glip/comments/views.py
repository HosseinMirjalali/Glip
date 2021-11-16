from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import get_object_or_404

from glip.comments.models import Comment


@login_required
def like_comment(request):
    if request.POST.get("action") == "post":
        result = ""
        comment_id = request.POST.get("comment_id")
        comment = get_object_or_404(Comment, id=comment_id)
        if comment.likes.filter(id=request.user.id).exists():
            comment.likes.remove(request.user)
            result = comment.likes.count()
            comment.save()
        else:
            comment.likes.add(request.user)
            result = comment.likes.count()
            comment.save()

        return JsonResponse({"result": result})
