from django.db import models

class Interaction(models.Model):
    timestamp = models.DateTimeField(auto_now_add=True)
    audio_filename = models.CharField(max_length=255, null=True, blank=True)
    transcription = models.TextField()
    ia_response = models.TextField()
    tts_audio_filename = models.CharField(max_length=255)

    def __str__(self):
        return f"Interacción #{self.id} - {self.timestamp.strftime('%Y-%m-%d %H:%M:%S')}"

class StaticResponse(models.Model):
    keyword = models.CharField(max_length=255, unique=True)
    answer = models.TextField()

    def __str__(self):
        return self.keyword

class KnowledgeBaseEntry(models.Model):
    title = models.CharField(max_length=255)
    content = models.TextField()
    tags = models.CharField(max_length=255, blank=True)  # Para búsquedas rápidas, opcional
    created_at = models.DateTimeField(auto_now_add=True)
