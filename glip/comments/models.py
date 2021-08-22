# from django.contrib.auth import get_user_model # noqa: E731
# from django.db import models # noqa: E731

# from glip.clips.models import Clip # noqa: E731

# User = get_user_model() # noqa: E731


# class Comment(models.Model): # noqa: E731
#     user = models.ForeignKey(User, on_delete=models.CASCADE) # noqa: E731
#     clip = models.ForeignKey(Clip, on_delete=models.CASCADE) # noqa: E731
#     reply = models.ForeignKey('self', null=True, related_name='replies', blank=True, on_delete=models.CASCADE)  # noqa: E731,E501
#     content = models.TextField(max_length=1000) # noqa: E731
#     timestamp = models.DateTimeField(auto_now_add=True) # noqa: E731
