"""
Vistas del agente de audio inteligente para Signaware.
Proporciona endpoints para procesamiento de audio y transcripción.
"""

import logging
import json
import soundfile as sf
import os
import uuid
import time
from datetime import datetime, timedelta
from django.http import JsonResponse, FileResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from langchain_core.messages import HumanMessage
from rest_framework.views import APIView
import dotenv
from rest_framework import viewsets
from .models import DetectedSound
from .serializers import DetectedSoundSerializer
from core.models import SoundCategory, SoundType
import numpy as np
from .logic.agent_manager import AgentManager
from .providers.text_generation.text_generator_manager import text_generator_manager

# Configurar logging
logger = logging.getLogger(__name__)

# Almacenamiento temporal de audios procesados (en producción usar base de datos)
processed_audios = {}


AGENT_MANAGER = AgentManager()


def normalize_sound_type_name(name):
    return name.strip().lower().replace(" ", "_")


class AgentView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user_message = request.data.get("message")
        model = request.data.get("model", "gemini")
        if not user_message:
            return Response({"error": "No se recibió mensaje."}, status=400)

        try:

            result = AGENT_MANAGER.execute_agent(
                agent_name="chatbot",
                user_input=user_message,
                text_generator_model=model,
            )

            # Si el resultado es un objeto con response y detected_intent
            if isinstance(result, dict):
                return Response(result)
            else:
                # Fallback para respuestas de texto simple
                return Response({"response": result, "detected_intent": "GENERAL_QUERY"})

        except Exception as e:
            logger.error(f"Error general en AgentView: {e}")
            return Response(
                {"error": f"Error interno del servidor: {str(e)}"}, status=500
            )


def cleanup_old_audios():
    """
    Limpia archivos de audio antiguos (más de 1 hora).
    """
    try:
        current_time = time.time()
        max_age = 3600  # 1 hora en segundos
        to_delete = []

        for audio_id, audio_info in processed_audios.items():
            # Verificar si el archivo existe y es antiguo
            if os.path.exists(audio_info["audio_path"]):
                file_age = current_time - os.path.getmtime(audio_info["audio_path"])
                if file_age > max_age:
                    to_delete.append(audio_id)
                    try:
                        os.unlink(audio_info["audio_path"])
                        logger.info(
                            f"Archivo antiguo eliminado: {audio_info['audio_path']}"
                        )
                    except Exception as e:
                        logger.error(
                            f"Error eliminando archivo {audio_info['audio_path']}: {e}"
                        )
            else:
                # El archivo no existe, eliminar de la lista
                to_delete.append(audio_id)

        # Eliminar entradas de la memoria
        for audio_id in to_delete:
            del processed_audios[audio_id]
            logger.info(f"Entrada eliminada de processed_audios: {audio_id}")

        if to_delete:
            logger.info(f"Limpieza completada: {len(to_delete)} archivos eliminados")

    except Exception as e:
        logger.error(f"Error en limpieza de archivos: {e}")


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def process_audio(request):
    """
    Endpoint para procesar audio y obtener transcripción.

    Espera recibir un archivo de audio y devuelve:
    - Tipo de sonido detectado
    - Transcripción (si es conversación)
    - Nivel de confianza
    - Mensajes del sistema
    - ID del audio para reproducir

    Args:
        request: Request HTTP con archivo de audio

    Returns:
        Response: JSON con resultados del procesamiento
    """
    try:
        logger.info("Iniciando procesamiento de audio")
        logger.info(f"Usuario: {request.user.id}")
        logger.info(f"Método: {request.method}")
        logger.info(f"Content-Type: {request.content_type}")
        logger.info(f"FILES keys: {list(request.FILES.keys())}")

        # Verificar que se envió un archivo de audio
        if "audio" not in request.FILES:
            logger.error("No se recibió archivo de audio")
            logger.error(f"Archivos recibidos: {list(request.FILES.keys())}")
            return Response(
                {"error": "Se requiere un archivo de audio"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        audio_file = request.FILES["audio"]
        logger.info(f"Archivo de audio recibido: {audio_file.name}")
        logger.info(f"Tamaño del archivo: {audio_file.size} bytes")
        logger.info(f"Content-Type del archivo: {audio_file.content_type}")

        # Validar tipo de archivo
        allowed_types = [
            "audio/wav",
            "audio/mp3",
            "audio/mpeg",
            "audio/ogg",
            "audio/x-wav",
            "audio/wave",
        ]
        file_content_type = audio_file.content_type.lower()

        # Verificar si el tipo está permitido directamente
        if file_content_type not in allowed_types:
            # Verificar si es un archivo WAV por extensión
            if audio_file.name.lower().endswith(".wav"):
                logger.info(
                    f"Archivo WAV detectado por extensión, Content-Type: {file_content_type}"
                )
            else:
                logger.error(f"Tipo de archivo no soportado: {file_content_type}")
                return Response(
                    {
                        "error": f"Tipo de archivo no soportado. Tipos permitidos: {', '.join(allowed_types)}"
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )

        # Verificar que el archivo no esté vacío
        if audio_file.size == 0:
            logger.error("Archivo de audio vacío")
            return Response(
                {"error": "El archivo de audio está vacío"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        logger.info(
            f"Archivo de audio válido: {audio_file.name} ({audio_file.size} bytes)"
        )

        # final_state = SOUND_DETECTOR_AGENT.execute(user_input=None, audio_path=audio_file.name, audio_file=audio_file)
        final_state = AGENT_MANAGER.execute_agent(
            agent_name="sound_detector",
            user_input=None,
            audio_path=audio_file.name,
            audio_file=audio_file,
        )
        # Generar ID único para el audio
        audio_id = str(uuid.uuid4())

        # Guardar información del audio procesado
        processed_audios[audio_id] = {
            "user_id": request.user.id,
            "audio_path": final_state.get("audio_path", ""),
            "timestamp": final_state.get("timestamp", ""),
            "sound_type": final_state.get("sound_type", "Unknown"),
        }

        # Guardar DetectedSound en la base de datos si el sonido es relevante
        sound_type = final_state.get("sound_type", "Unknown")
        alert_category = final_state.get("alert_category", "unknown")
        confidence = final_state.get("confidence", 0.0)
        transcription = final_state.get("transcription", "")
        raw_data = final_state.get("sound_detections", [])
        audio_path = final_state.get("audio_path", "")

        # Inicializar variables para el label en español
        sound_type_label = "Desconocido"  # Valor por defecto
        sound_type_obj = None

        if sound_type.lower() != "unknown":
            import traceback

            logger.debug(
                f"Intentando guardar DetectedSound: sound_type={sound_type}, alert_category={alert_category}, confidence={confidence}, transcription={transcription}"
            )

            try:
                category_obj = SoundCategory.objects.get(name=alert_category)
                normalized_name = normalize_sound_type_name(sound_type)
                # Buscar el SoundType por nombre normalizado
                try:
                    sound_type_obj = SoundType.objects.get(name=normalized_name)
                    sound_type_label = (
                        sound_type_obj.label
                    )  # Obtener el label en español
                except SoundType.DoesNotExist:
                    # Si no existe, crear uno nuevo SOLO para pruebas/desarrollo
                    sound_type_obj = SoundType.objects.create(
                        name=normalized_name,
                        label=sound_type,  # Si no hay label en español, usar el detectado
                        description=f"Sonido detectado: {sound_type}",
                        is_critical=alert_category
                        in ["siren", "car_horn", "gun_shot", "glass_breaking"],
                    )
                    sound_type_label = sound_type_obj.label
                try:
                    ds = DetectedSound.objects.create(
                        user=request.user,
                        sound_type=sound_type_obj,
                        category=category_obj,
                        confidence=confidence,
                        transcription=transcription,
                    )
                    logger.info(f"DetectedSound guardado correctamente: {ds}")
                except Exception as e:
                    logger.error(
                        f"Error al guardar DetectedSound: {e}\n{traceback.format_exc()}"
                    )
            except SoundCategory.DoesNotExist:
                logger.warning(
                    f"No se encontró la categoría '{alert_category}' para el sonido detectado. No se guardó DetectedSound."
                )
            except Exception as e:
                logger.error(
                    f"Error inesperado al buscar categoría o guardar DetectedSound: {e}\n{traceback.format_exc()}"
                )

        # Preparar respuesta - solo incluir mensajes únicos y relevantes
        messages = final_state.get("messages", [])
        unique_messages = []
        seen_contents = set()

        for msg in messages:
            if msg.content not in seen_contents:
                unique_messages.append(msg)
                seen_contents.add(msg.content)

        response_data = {
            "success": True,
            "user_id": request.user.id,
            "audio_id": audio_id,
            "sound_type": final_state.get("sound_type", "Unknown"),
            "sound_type_label": sound_type_label,  # <-- SIEMPRE INCLUIR EL LABEL EN ESPAÑOL
            "confidence": final_state.get("confidence", 0.0),
            "alert_category": final_state.get("alert_category", "unknown"),
            "is_conversation_detected": final_state.get(
                "is_conversation_detected", False
            ),
            "transcription": final_state.get("transcription", ""),
            "sound_detections": final_state.get("sound_detections", []),
            "messages": [
                {
                    "type": "system" if "ERROR" in msg.content else "info",
                    "content": msg.content,
                }
                for msg in unique_messages
            ],
        }

        logger.info(
            f"Procesamiento completado: {response_data['sound_type']} (confianza: {response_data['confidence']:.2f})"
        )
        logger.info(f"Audio ID generado: {audio_id}")

        # Limpiar archivos antiguos
        cleanup_old_audios()

        return Response(response_data, status=status.HTTP_200_OK)

    except Exception as e:
        logger.error(f"Error en procesamiento de audio: {e}")
        logger.exception("Traceback completo:")
        return Response(
            {"error": "Error interno del servidor", "details": str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_audio(request, audio_id):
    """
    Endpoint para obtener el audio procesado.

    Args:
        request: Request HTTP
        audio_id: ID único del audio procesado

    Returns:
        FileResponse: Archivo de audio
    """
    try:
        logger.info(f"Intentando obtener audio: {audio_id}")
        logger.info(f"Usuario solicitante: {request.user.id}")
        logger.info(f"Audios disponibles: {list(processed_audios.keys())}")

        # Verificar que el audio existe y pertenece al usuario
        if audio_id not in processed_audios:
            logger.error(f"Audio {audio_id} no encontrado en processed_audios")
            return Response(
                {"error": "Audio no encontrado"}, status=status.HTTP_404_NOT_FOUND
            )

        audio_info = processed_audios[audio_id]
        logger.info(f"Información del audio: {audio_info}")

        # Verificar que el usuario tiene acceso al audio
        if audio_info["user_id"] != request.user.id:
            logger.error(
                f"Usuario {request.user.id} no tiene acceso al audio {audio_id}"
            )
            return Response(
                {"error": "Acceso denegado"}, status=status.HTTP_403_FORBIDDEN
            )

        audio_path = audio_info["audio_path"]
        logger.info(f"Ruta del archivo: {audio_path}")

        # Verificar que el archivo existe
        if not os.path.exists(audio_path):
            logger.error(f"Archivo no encontrado en disco: {audio_path}")
            return Response(
                {"error": "Archivo de audio no encontrado en el servidor"},
                status=status.HTTP_404_NOT_FOUND,
            )

        file_size = os.path.getsize(audio_path)
        logger.info(f"Tamaño del archivo: {file_size} bytes")

        if file_size == 0:
            logger.error(f"Archivo vacío: {audio_path}")
            return Response(
                {"error": "Archivo de audio está vacío"},
                status=status.HTTP_404_NOT_FOUND,
            )

        # Servir el archivo de audio
        try:
            response = FileResponse(open(audio_path, "rb"), content_type="audio/wav")
            response["Content-Disposition"] = (
                f'attachment; filename="audio_{audio_id}.wav"'
            )
            response["Content-Length"] = file_size

            logger.info(f"Archivo enviado exitosamente: {audio_id} ({file_size} bytes)")
            return response

        except Exception as e:
            logger.error(f"Error al abrir/leer archivo {audio_path}: {e}")
            return Response(
                {"error": "Error al leer el archivo de audio"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    except Exception as e:
        logger.error(f"Error al servir audio {audio_id}: {e}")
        logger.exception("Traceback completo:")
        return Response(
            {"error": "Error al servir el audio"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def health_check(request):
    """
    Endpoint para verificar el estado del agente de audio.

    Returns:
        Response: Estado del sistema de procesamiento de audio
    """
    try:
        status_data = {
            "status": "healthy" if compiled_workflow is not None else "unavailable",
            "workflow_compiled": compiled_workflow is not None,
            "user_id": request.user.id,
        }

        return Response(status_data, status=status.HTTP_200_OK)

    except Exception as e:
        logger.error(f"Error en health check: {e}")
        return Response(
            {"status": "error", "error": str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


@csrf_exempt
@require_http_methods(["POST"])
def process_audio_legacy(request):
    """
    Endpoint legacy para compatibilidad con clientes que no usan DRF.

    Args:
        request: Request HTTP con archivo de audio

    Returns:
        JsonResponse: JSON con resultados del procesamiento
    """
    try:
        logger.info("Iniciando procesamiento de audio (legacy)")

        # Verificar que el workflow esté disponible
        if compiled_workflow is None:
            logger.error("Workflow no disponible")
            return JsonResponse(
                {"error": "Sistema de procesamiento de audio no disponible"}, status=503
            )

        # Verificar que se envió un archivo de audio
        if "audio" not in request.FILES:
            logger.error("No se recibió archivo de audio")
            return JsonResponse(
                {"error": "Se requiere un archivo de audio"}, status=400
            )

        audio_file = request.FILES["audio"]

        # Ejecutar el workflow del agente
        initial_state = get_initial_state()
        initial_state["audio_file"] = audio_file

        final_state = compiled_workflow.invoke(initial_state)

        # Preparar respuesta
        response_data = {
            "success": True,
            "sound_type": final_state.get("sound_type", "Unknown"),
            "confidence": final_state.get("confidence", 0.0),
            "is_conversation_detected": final_state.get(
                "is_conversation_detected", False
            ),
            "transcription": final_state.get("transcription", ""),
            "messages": [
                {
                    "type": "system" if "ERROR" in msg.content else "info",
                    "content": msg.content,
                }
                for msg in final_state.get("messages", [])
            ],
        }

        logger.info(f"Procesamiento completado (legacy): {response_data['sound_type']}")

        return JsonResponse(response_data, status=200)

    except Exception as e:
        logger.error(f"Error en procesamiento de audio (legacy): {e}")
        return JsonResponse(
            {"error": "Error interno del servidor", "details": str(e)}, status=500
        )


class DetectedSoundViewSet(viewsets.ModelViewSet):
    queryset = DetectedSound.objects.none()  # Necesario para DRF basename
    serializer_class = DetectedSoundSerializer

    def get_queryset(self):
        return DetectedSound.objects.filter(user=self.request.user).order_by(
            "-timestamp"
        )

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)



