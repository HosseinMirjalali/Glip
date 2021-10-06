from django import forms

from glip.comments.models import Comment


class NewCommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ("content",)
        widgets = {
            "content": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "placeholder": "Your comment...",
                    "rows": 4,
                    "cols": 10,
                }
            )
        }
        labels = {"content": ""}
