import os
import re
import unicodedata
import shutil
from datetime import datetime
from django.http import FileResponse, JsonResponse, Http404
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from rest_framework.decorators import api_view, parser_classes
from rest_framework.parsers import MultiPartParser, JSONParser
from rest_framework.response import Response
from rest_framework import status
from .models import Interaction, StaticResponse
from .serializers import TextToSpeechInputSerializer, StaticResponseCreateSerializer
from dotenv import load_dotenv
import openai

load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

AUDIO_DIR = os.path.join(settings.MEDIA_ROOT, "audios")
RESPONSE_DIR = os.path.join(settings.MEDIA_ROOT, "responses")
os.makedirs(AUDIO_DIR, exist_ok=True)
os.makedirs(RESPONSE_DIR, exist_ok=True)

def slugify(text: str) -> str:
    text = unicodedata.normalize('NFKD', text)
    text = text.encode('ascii', 'ignore').decode('utf-8')
    text = re.sub(r'[^\w\s-]', '', text).strip().lower()
    return re.sub(r'[-\s]+', '-', text)

@api_view(['POST'])
@parser_classes([MultiPartParser])
def ask_ai(request):
    file = request.FILES.get('file')
    if not file:
        return Response({'detail': 'Archivo no enviado'}, status=400)

    ext = file.name.split('.')[-1]
    input_filename = f"{datetime.utcnow().strftime('%Y%m%d%H%M%S%f')}.{ext}"
    input_path = os.path.join(AUDIO_DIR, input_filename)

    with open(input_path, 'wb') as buffer:
        shutil.copyfileobj(file, buffer)

    try:
        with open(input_path, "rb") as audio_file:
            transcript = openai.audio.transcriptions.create(
                model="whisper-1",
                file=audio_file,
                response_format="text"
            )
        texto_transcrito = transcript.strip()
    except Exception as e:
        return Response({'detail': f'Error transcribiendo: {str(e)}'}, status=500)

    static = StaticResponse.objects.all()
    ia_response = None
    for sr in static:
        if sr.keyword.lower() in texto_transcrito.lower():
            ia_response = sr.answer
            break

    if ia_response is None:
        try:
            response = openai.chat.completions.create(
                model="gpt-4o",
                messages=[{"role": "user", "content": texto_transcrito}]
            )
            ia_response = response.choices[0].message.content.strip()
        except Exception as e:
            return Response({'detail': f'Error con GPT-4o: {str(e)}'}, status=500)

    try:
        tts_audio_filename = f"response_{datetime.utcnow().strftime('%Y%m%d%H%M%S%f')}.mp3"
        tts_audio_path = os.path.join(RESPONSE_DIR, tts_audio_filename)
        tts_response = openai.audio.speech.create(
            model="tts-1",
            voice="alloy",
            input=ia_response
        )
        with open(tts_audio_path, "wb") as f:
            f.write(tts_response.content)
    except Exception as e:
        return Response({'detail': f'Error generando audio TTS: {str(e)}'}, status=500)

    Interaction.objects.create(
        audio_filename=input_filename,
        transcription=texto_transcrito,
        ia_response=ia_response,
        tts_audio_filename=tts_audio_filename
    )

    return FileResponse(open(tts_audio_path, 'rb'), content_type="audio/mpeg", filename=tts_audio_filename)

@api_view(['POST'])
@parser_classes([JSONParser])
def text_to_speech(request):
    serializer = TextToSpeechInputSerializer(data=request.data)
    if serializer.is_valid():
        text = serializer.validated_data['text']
        if not text.strip():
            return Response({'detail': 'Texto vacío'}, status=400)

        try:
            tts_audio_filename = f"tts_{datetime.utcnow().strftime('%Y%m%d%H%M%S%f')}.mp3"
            tts_audio_path = os.path.join(RESPONSE_DIR, tts_audio_filename)
            tts_response = openai.audio.speech.create(
                model="tts-1",
                voice="alloy",
                input=text
            )
            with open(tts_audio_path, "wb") as f:
                f.write(tts_response.content)

            Interaction.objects.create(
                transcription=text,
                ia_response=text,
                tts_audio_filename=tts_audio_filename
            )

            return FileResponse(open(tts_audio_path, 'rb'), content_type="audio/mpeg", filename=tts_audio_filename)
        except Exception as e:
            return Response({'detail': f'Error generando audio: {str(e)}'}, status=500)
    return Response(serializer.errors, status=400)

@api_view(['GET'])
def get_audio_from_question(request):
    question = request.GET.get('question')
    if not question:
        return Response({'detail': 'Falta parámetro ?question'}, status=400)
    slug = slugify(question)
    filename = f"{slug}.mp3"
    filepath = os.path.join(RESPONSE_DIR, filename)
    if not os.path.exists(filepath):
        raise Http404("No se encontró audio para esta pregunta")
    return FileResponse(open(filepath, 'rb'), content_type="audio/mpeg", filename=filename)

@api_view(['POST'])
@parser_classes([JSONParser])
def create_static_response(request):
    serializer = StaticResponseCreateSerializer(data=request.data)
    if serializer.is_valid():
        keyword = serializer.validated_data['keyword']
        if StaticResponse.objects.filter(keyword=keyword).exists():
            return Response({'detail': 'Keyword ya existe'}, status=400)
        serializer.save()
        return Response(serializer.data)
    return Response(serializer.errors, status=400)

@api_view(['GET'])
def get_last_audio_path(request):
    last = Interaction.objects.order_by('-timestamp').first()
    if not last:
        return Response({'detail': 'No hay interacciones'}, status=404)
    return JsonResponse({
        'audio_path': f"/media/responses/{last.tts_audio_filename}"
    })
