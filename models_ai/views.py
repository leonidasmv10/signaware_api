from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.parsers import JSONParser
from rest_framework import status
import tensorflow_hub as hub
import tensorflow as tf
import tempfile
import os
import numpy as np
import librosa
from django.utils import timezone
from detections.models import (
    AudioDetection,
    SoundType,
    Location,
    VisualDetection,
    VehicleType,
)

import base64
import re

from .yolo_predict import predict_image

# Load model once when the server starts
MODEL_PATH = "models_ai/models/critical_sound_detector_model.h5"
model = tf.keras.models.load_model(MODEL_PATH)

# Class labels
LABELS = ["Bocina", "Sirena", "null"]

# Load YAMNet model from TensorFlow Hub
yamnet_model = hub.load("https://tfhub.dev/google/yamnet/1")


class DetectionCriticalSoundAPIView(APIView):
    """API view for critical sound detection from audio files."""

    def post(self, request):
        """Process uploaded audio file and detect critical sounds.

        Args:
            request: HTTP request containing audio file and location data

        Returns:
            Response: Detection results with status code
        """
        # Validate audio file
        audio_file = request.FILES.get("audio")
        if not audio_file:
            return Response(
                {
                    "error": "No audio file provided.",
                    "timestamp": timezone.now().isoformat(),
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            # Process audio file
            temp_audio_path = self._save_temp_audio(audio_file)

            # Extract audio features
            audio_features = self._extract_audio_features(temp_audio_path)

            # Make predictions
            predictions = model.predict(np.array([audio_features]))[0]

            # Process results
            sorted_results = self._process_prediction_results(predictions)
            predicted_label = sorted_results[0]["label"]
            predicted_score = sorted_results[0]["score"]

            # Prepare response data
            response_data = {
                "results": sorted_results,
                "predicted_label": predicted_label,
                "predicted_score": predicted_score,
            }

            # Save data to database only if not "null"
            if predicted_label != "null":
                data_result = self._save_detection_data(request, predicted_label)
                # Add database IDs to response only if data was saved
                if data_result:
                    location, audio_detection = data_result
                    response_data.update(
                        {
                            "location_id": location.id,
                            "audio_detection_id": audio_detection.id,
                            "detection_date": audio_detection.detection_date.isoformat(),
                        }
                    )

            # Clean up temporary file
            os.remove(temp_audio_path)

            return Response(response_data, status=status.HTTP_201_CREATED)

        except Exception as e:
            return Response(
                {
                    "error": f"Internal error: {str(e)}",
                    "timestamp": timezone.now().isoformat(),
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    def _save_temp_audio(self, audio_file):
        """Save uploaded audio to temporary file.

        Args:
            audio_file: The uploaded audio file

        Returns:
            str: Path to temporary audio file
        """
        temp_audio = tempfile.NamedTemporaryFile(delete=False, suffix=".wav")
        for chunk in audio_file.chunks():
            temp_audio.write(chunk)
        temp_audio.flush()
        temp_audio.close()
        return temp_audio.name

    def _extract_audio_features(self, audio_path):
        """Extract audio features using YAMNet model.

        Args:
            audio_path: Path to audio file

        Returns:
            numpy.ndarray: Audio embedding features
        """
        audio, _ = librosa.load(audio_path, sr=16000)
        _, embeddings, _ = yamnet_model(audio)
        audio_embedding = tf.reduce_mean(embeddings, axis=0).numpy()
        return audio_embedding

    def _process_prediction_results(self, predictions):
        """Process model predictions and format results.

        Args:
            predictions: Model prediction results

        Returns:
            list: Sorted prediction results with labels and scores
        """
        # Pair labels with predictions
        paired_results = list(zip(LABELS, predictions))

        # Sort by confidence score (highest first)
        sorted_pairs = sorted(paired_results, key=lambda x: x[1], reverse=True)

        # Format results
        formatted_results = [
            {"label": label, "score": float(f"{score:.4f}")}
            for label, score in sorted_pairs
        ]

        return formatted_results

    def _save_detection_data(self, request, label):
        """Save detection results to database.

        Args:
            request: HTTP request containing user and location data
            label: Predicted sound label

        Returns:
            tuple: (location_object, audio_detection_object) or None if label is "null"
        """
        # Don't save data if the label is "null"
        if label == "null":
            return None

        # Save location data
        location_result = Location.objects.create(
            user=request.user,
            latitud=request.data.get("latitude") or 9999,
            longitud=request.data.get("longitude") or 9999,
            date=timezone.now(),
        )

        # Save audio detection
        audio_detection_result = AudioDetection.objects.create(
            user=request.user,
            sound_type=SoundType.objects.get(type_name=label),
            location=location_result,  # Use the object directly
            detection_date=timezone.now(),
        )

        return (location_result, audio_detection_result)


class RealTimeDetectionView(APIView):
    parser_classes = [JSONParser]

    def post(self, request):
        image_data = request.data.get("image", "")

        # Extraer la parte de base64
        match = re.search(r"base64,(.*)", image_data)
        if not match:
            return Response({"error": "Imagen base64 no válida"}, status=400)

        try:
            image_bytes = base64.b64decode(match.group(1))
            detections = predict_image(image_bytes)

            if detections:
                label = detections[0]["label"]
                # print("label: ", detections[0]["label"])
                if label != "person":

                    visual_detection_result = VisualDetection.objects.create(
                        user=request.user,
                        vehicle_type=VehicleType.objects.get(type_name=label),
                        frequency=0,
                        detection_date=timezone.now(),
                    )

            return Response({"detections": detections, "alert": bool(detections)})
        except Exception as e:
            return Response({"error": str(e)}, status=500)
