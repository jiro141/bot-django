from rest_framework import serializers
from .models import StaticResponse

class TextToSpeechInputSerializer(serializers.Serializer):
    text = serializers.CharField()

class StaticResponseCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = StaticResponse
        fields = ['keyword', 'answer']
