from django.urls import path
from . import views

urlpatterns = [
    path('ask/', views.ask_ai),
    path('text-to-speech/', views.text_to_speech),  # 👈 ESTA ES LA QUE FALTA SEGURAMENTE
    path('audio-from-question/', views.get_audio_from_question),
    path('static-response/', views.create_static_response),
    path('last-audio-file-path/', views.get_last_audio_path),
]
