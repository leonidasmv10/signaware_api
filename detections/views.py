from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView
from .serializers import (
    VisualDetectionSerializer,
    LocationSerializer,
    AudioDetectionSerializer,
)
from .models import AudioDetection, VisualDetection, Location
from django.utils import timezone
from datetime import date
from collections import defaultdict
import requests
import time
import math


class VisualDetectionCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = VisualDetectionSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(user=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class AudioDetectionCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = AudioDetectionSerializer(data=request.data)
        if serializer.is_valid():
            audio_detection = serializer.save(user=request.user)
            return Response(
                {
                    **serializer.data,
                    "creation_timestamp": timezone.localtime(
                        audio_detection.detection_date
                    ).isoformat(),
                },
                status=status.HTTP_201_CREATED,
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LocationCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = LocationSerializer(data=request.data)
        if serializer.is_valid():
            location = serializer.save(user=request.user)
            return Response(
                {
                    **serializer.data,  # Datos serializados
                    # "creation_timestamp": location.date.isoformat(),
                },
                status=status.HTTP_201_CREATED,
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class AudioDetectionListView(APIView):
    def get(self, request):
        # Obtiene todas las detecciones de audio sin filtrar por usuario
        audio_detections = AudioDetection.objects.all()
        serializer = AudioDetectionSerializer(audio_detections, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class DailySummaryView(APIView):
    permission_classes = [IsAuthenticated]

    def __init__(self):
        super().__init__()
        self.address_cache = {}  # Cache para almacenar direcciones ya obtenidas

    def get_address_from_coordinates(self, lat, lon):
        # Crear una clave única para las coordenadas
        coord_key = f"{lat:.6f},{lon:.6f}"
        
        # Si ya tenemos la dirección en cache, retornarla
        if coord_key in self.address_cache:
            return self.address_cache[coord_key]
            
        try:
            headers = {
                'User-Agent': 'SafeDriveApp/1.0 (yordy@example.com)'
            }
            url = f"https://nominatim.openstreetmap.org/reverse?format=jsonv2&lat={lat}&lon={lon}"
            
            # Añadir un pequeño retraso para cumplir con las políticas de uso
            time.sleep(1)
            
            response = requests.get(url, headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                address = data.get('display_name', 'Dirección no disponible')
                # Guardar en cache
                self.address_cache[coord_key] = address
                return address
            elif response.status_code == 429:
                return 'Límite de peticiones alcanzado'
            else:
                return f'Error al obtener la dirección (código: {response.status_code})'
        except requests.exceptions.RequestException as e:
            return f'Error de conexión: {str(e)}'
        except Exception as e:
            return f'Error inesperado: {str(e)}'

    def haversine_distance(self, lat1, lon1, lat2, lon2):
        # Radio de la Tierra en kilómetros
        R = 6371.0
        
        # Convertir grados a radianes
        lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])
        
        # Diferencias
        dlat = lat2 - lat1
        dlon = lon2 - lon1
        
        # Fórmula de Haversine
        a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
        distance = R * c
        
        return distance

    def group_nearby_locations(self, locations, max_distance_km=0.1):
        groups = []
        used_indices = set()
        
        for i, loc1 in enumerate(locations):
            if i in used_indices:
                continue
                
            group = [loc1]
            used_indices.add(i)
            
            for j, loc2 in enumerate(locations[i+1:], start=i+1):
                if j in used_indices:
                    continue
                    
                distance = self.haversine_distance(
                    loc1['lat'], loc1['lon'],
                    loc2['lat'], loc2['lon']
                )
                
                if distance <= max_distance_km:
                    group.append(loc2)
                    used_indices.add(j)
            
            if len(group) > 1:  # Solo incluir grupos con más de una detección
                groups.append(group)
        
        return groups

    def get(self, request):
        user = request.user
        today = date.today()
        critical_areas = []  # Definir critical_areas al inicio

        # Obtener todas las detecciones del día para el usuario
        audio_detections = AudioDetection.objects.filter(
            user=user, detection_date__date=today
        ).select_related('location', 'sound_type')
        visual_detections = VisualDetection.objects.filter(
            user=user, detection_date__date=today
        ).select_related('vehicle_type')

        # Contar tipos de sonidos con ubicación
        sounds_counter = {}
        sound_locations = defaultdict(list)
        raw_locations = []  # Para almacenar las coordenadas originales
        location_data = {}  # Para almacenar datos de ubicación ya procesados

        for detection in audio_detections:
            sound_type_name = (
                detection.sound_type.type_name if detection.sound_type else "null"
            )
            sounds_counter[sound_type_name] = sounds_counter.get(sound_type_name, 0) + 1
            
            # Agregar ubicación del sonido
            if detection.location:
                coord_key = f"{detection.location.latitud:.6f},{detection.location.longitud:.6f}"
                
                # Si ya procesamos esta ubicación, reutilizar los datos
                if coord_key in location_data:
                    address = location_data[coord_key]['address']
                else:
                    address = self.get_address_from_coordinates(
                        detection.location.latitud, 
                        detection.location.longitud
                    )
                    location_data[coord_key] = {
                        'address': address,
                        'lat': detection.location.latitud,
                        'lon': detection.location.longitud
                    }

                sound_locations[sound_type_name].append({
                    'address': address,
                    'time': detection.detection_date.strftime('%H:%M')
                })
                
                # Guardar las coordenadas originales para el análisis de proximidad
                raw_locations.append({
                    'lat': detection.location.latitud,
                    'lon': detection.location.longitud,
                    'address': address,
                    'time': detection.detection_date.strftime('%H:%M'),
                    'sound_type': sound_type_name
                })

        # Contar tipos de vehículos con tiempo
        vehicles_counter = {}
        vehicle_times = defaultdict(list)
        for detection in visual_detections:
            vehicle_label = (
                detection.vehicle_type.type_name if detection.vehicle_type else "null"
            )
            vehicles_counter[vehicle_label] = vehicles_counter.get(vehicle_label, 0) + 1
            vehicle_times[vehicle_label].append({
                'time': detection.detection_date.strftime('%H:%M')
            })

        # Crear resumen detallado
        summary_data = {
            "date": today.isoformat(),
            "sounds": [],
            "vehicles": [],
            "heatmap_data": [],
            "critical_areas": []
        }

        # Sonidos detectados con ubicaciones
        if sounds_counter:
            for sound, count in sounds_counter.items():
                summary_data["sounds"].append({
                    "label": sound,
                    "count": count,
                    "locations": sound_locations[sound]
                })
        else:
            summary_data["sounds"] = [
                {"label": "No se detectaron sonidos críticos", "count": 0, "locations": []}
            ]

        # Vehículos detectados con tiempos
        if vehicles_counter:
            for vehicle, count in vehicles_counter.items():
                summary_data["vehicles"].append({
                    "label": vehicle,
                    "count": count,
                    "times": vehicle_times[vehicle]
                })
        else:
            summary_data["vehicles"] = [
                {"label": "No se detectaron vehículos críticos", "count": 0, "times": []}
            ]

        # Generar datos para el heatmap (solo audio)
        all_locations = []
        for detection in audio_detections:
            if detection.location:
                coord_key = f"{detection.location.latitud:.6f},{detection.location.longitud:.6f}"
                location_info = location_data[coord_key]
                
                all_locations.append({
                    'address': location_info['address'],
                    'time': detection.detection_date.strftime('%H:%M'),
                    'type': 'audio',
                    'sound_type': detection.sound_type.type_name if detection.sound_type else 'unknown'
                })

        summary_data["heatmap_data"] = all_locations

        # Identificar áreas críticas basadas en proximidad
        if raw_locations:
            location_groups = self.group_nearby_locations(raw_locations)
            
            for group in location_groups:
                # Calcular el centro del grupo
                avg_lat = sum(loc['lat'] for loc in group) / len(group)
                avg_lon = sum(loc['lon'] for loc in group) / len(group)
                
                # Obtener la dirección del centro
                center_address = self.get_address_from_coordinates(avg_lat, avg_lon)
                
                # Obtener los tipos de sonidos en el área
                sound_types = set(loc['sound_type'] for loc in group)
                
                critical_areas.append({
                    'address': center_address,
                    'detection_count': len(group),
                    'sound_types': list(sound_types),
                    'times': [loc['time'] for loc in group],
                    'center_lat': avg_lat,
                    'center_lon': avg_lon
                })

        summary_data["critical_areas"] = critical_areas

        return Response(summary_data, status=status.HTTP_200_OK)
