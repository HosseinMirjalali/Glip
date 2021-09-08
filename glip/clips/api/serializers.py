from rest_framework import serializers

from glip.clips.models import Clip


class ClipSerializer(serializers.ModelSerializer):
    class Meta:
        model = Clip
        fields = "__all__"
