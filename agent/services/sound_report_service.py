"""
Servicio para generar reportes de sonidos detectados.
"""

from django.db import models
from django.db.models import Count, Avg, Min, Max
from django.utils import timezone
from datetime import datetime, timedelta
from typing import Dict, List, Any
import logging

from ..models import DetectedSound
from core.models import SoundCategory, SoundType

logger = logging.getLogger(__name__)


class SoundReportService:
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def generate_sound_report(self, user_id: int = None, days: int = 30) -> Dict[str, Any]:
        """
        Genera un reporte completo de sonidos detectados.
        
        Args:
            user_id: ID del usuario (opcional, si no se proporciona se incluyen todos)
            days: Número de días hacia atrás para el reporte
            
        Returns:
            Dict con el reporte completo
        """
        try:
            # Validar parámetros
            if days <= 0:
                days = 30
            
            # Calcular fecha de inicio
            start_date = timezone.now() - timedelta(days=days)
            
            # Filtrar sonidos detectados
            queryset = DetectedSound.objects.filter(timestamp__gte=start_date)
            if user_id:
                queryset = queryset.filter(user_id=user_id)
            
            # Filtrar sonidos de speech/conversación del total
            filtered_queryset = queryset.exclude(
                models.Q(sound_type__name__icontains='speech') |
                models.Q(sound_type__name__icontains='conversation') |
                models.Q(sound_type__name__icontains='conversación') |
                models.Q(sound_type__label__icontains='speech') |
                models.Q(sound_type__label__icontains='conversation') |
                models.Q(sound_type__label__icontains='conversación')
            )
            
            # Verificar si hay datos
            if not filtered_queryset.exists():
                return {
                    "period": {
                        "start_date": start_date.strftime("%Y-%m-%d %H:%M:%S"),
                        "end_date": timezone.now().strftime("%Y-%m-%d %H:%M:%S"),
                        "days": days
                    },
                    "summary": {
                        "total_detections": 0,
                        "unique_sound_types": 0,
                        "average_confidence": 0
                    },
                    "sound_type_statistics": [],
                    "category_statistics": [],
                    "critical_sounds": [],
                    "temporal_patterns": {
                        "hourly_pattern": [],
                        "daily_pattern": [],
                        "last_24h_detections": 0
                    },
                    "recommendations": [
                        "📊 No se encontraron detecciones de sonidos en el período especificado.",
                        "💡 Considera verificar que el sistema de detección esté funcionando correctamente."
                    ]
                }
            
            # Obtener estadísticas generales
            total_detections = filtered_queryset.count()
            unique_sounds = filtered_queryset.values('sound_type__name').distinct().count()
            
            # Estadísticas por tipo de sonido
            sound_type_stats = self._get_sound_type_statistics(queryset)
            
            # Estadísticas por categoría
            category_stats = self._get_category_statistics(queryset)
            
            # Sonidos críticos
            critical_sounds = self._get_critical_sounds(queryset)
            
            # Patrones temporales
            temporal_patterns = self._get_temporal_patterns(filtered_queryset)
            
            # Recomendaciones
            recommendations = self._generate_recommendations(
                sound_type_stats, category_stats, critical_sounds, temporal_patterns
            )
            
            report = {
                "period": {
                    "start_date": start_date.strftime("%Y-%m-%d %H:%M:%S"),
                    "end_date": timezone.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "days": days
                },
                "summary": {
                    "total_detections": total_detections,
                    "unique_sound_types": unique_sounds,
                    "average_confidence": filtered_queryset.aggregate(Avg('confidence'))['confidence__avg'] or 0
                },
                "sound_type_statistics": sound_type_stats,
                "category_statistics": category_stats,
                "critical_sounds": critical_sounds,
                "temporal_patterns": temporal_patterns,
                "recommendations": recommendations
            }
            
            return report
            
        except Exception as e:
            self.logger.error(f"Error generando reporte de sonidos: {e}")
            return {
                "error": f"Error generando reporte: {str(e)}",
                "period": {
                    "start_date": (timezone.now() - timedelta(days=days)).strftime("%Y-%m-%d %H:%M:%S"),
                    "end_date": timezone.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "days": days
                },
                "summary": {"total_detections": 0},
                "sound_type_statistics": [],
                "category_statistics": [],
                "critical_sounds": [],
                "temporal_patterns": {
                    "hourly_pattern": [],
                    "daily_pattern": [],
                    "last_24h_detections": 0
                },
                "recommendations": [
                    "❌ Error al generar el reporte. Verifica la conexión a la base de datos."
                ]
            }
    
    def _get_sound_type_statistics(self, queryset) -> List[Dict[str, Any]]:
        """Obtiene estadísticas detalladas por tipo de sonido"""
        # Filtrar sonidos de speech/conversación
        filtered_queryset = queryset.exclude(
            models.Q(sound_type__name__icontains='speech') |
            models.Q(sound_type__name__icontains='conversation') |
            models.Q(sound_type__name__icontains='conversación') |
            models.Q(sound_type__label__icontains='speech') |
            models.Q(sound_type__label__icontains='conversation') |
            models.Q(sound_type__label__icontains='conversación')
        )
        
        stats = filtered_queryset.values(
            'sound_type__name', 
            'sound_type__label',
            'sound_type__is_critical'
        ).annotate(
            count=Count('id'),
            avg_confidence=Avg('confidence'),
            min_confidence=Min('confidence'),
            max_confidence=Max('confidence')
        ).order_by('-count')
        
        return [
            {
                "sound_type": stat['sound_type__name'],
                "label": stat['sound_type__label'],
                "is_critical": stat['sound_type__is_critical'],
                "count": stat['count'],
                "avg_confidence": round(stat['avg_confidence'], 3),
                "min_confidence": round(stat['min_confidence'], 3),
                "max_confidence": round(stat['max_confidence'], 3)
            }
            for stat in stats
        ]
    
    def _get_category_statistics(self, queryset) -> List[Dict[str, Any]]:
        """Obtiene estadísticas por categoría de sonido"""
        stats = queryset.values(
            'category__name', 
            'category__label',
            'category__emoji',
            'category__is_critical'
        ).annotate(
            count=Count('id'),
            avg_confidence=Avg('confidence')
        ).order_by('-count')
        
        return [
            {
                "category": stat['category__name'],
                "label": stat['category__label'],
                "emoji": stat['category__emoji'] or "🔊",
                "is_critical": stat['category__is_critical'],
                "count": stat['count'],
                "avg_confidence": round(stat['avg_confidence'], 3)
            }
            for stat in stats
        ]
    
    def _get_critical_sounds(self, queryset) -> List[Dict[str, Any]]:
        """Obtiene sonidos críticos detectados"""
        # Filtrar sonidos de speech/conversación
        filtered_queryset = queryset.exclude(
            models.Q(sound_type__name__icontains='speech') |
            models.Q(sound_type__name__icontains='conversation') |
            models.Q(sound_type__name__icontains='conversación') |
            models.Q(sound_type__label__icontains='speech') |
            models.Q(sound_type__label__icontains='conversation') |
            models.Q(sound_type__label__icontains='conversación')
        )
        
        critical_sounds = filtered_queryset.filter(
            models.Q(sound_type__is_critical=True) | 
            models.Q(category__is_critical=True)
        ).select_related('sound_type', 'category').order_by('-timestamp')
        
        return [
            {
                "sound_type": sound.sound_type.label,
                "category": sound.category.label,
                "confidence": round(sound.confidence, 3),
                "timestamp": sound.timestamp.strftime("%Y-%m-%d %H:%M:%S"),
                "transcription": sound.transcription or "N/A"
            }
            for sound in critical_sounds[:10]  # Top 10 sonidos críticos
        ]
    
    def _get_temporal_patterns(self, queryset) -> Dict[str, Any]:
        """Obtiene patrones temporales de detección"""
        # Últimas 24 horas
        last_24h = queryset.filter(
            timestamp__gte=timezone.now() - timedelta(hours=24)
        ).count()
        
        # Últimos 7 días
        last_7d = queryset.filter(
            timestamp__gte=timezone.now() - timedelta(days=7)
        ).count()
        
        # Últimos 30 días
        last_30d = queryset.filter(
            timestamp__gte=timezone.now() - timedelta(days=30)
        ).count()
        
        # Detecciones por día (últimos 7 días)
        daily_detections = []
        for i in range(7):
            date = timezone.now().date() - timedelta(days=i)
            count = queryset.filter(
                timestamp__date=date
            ).count()
            daily_detections.append({
                "date": date.strftime("%Y-%m-%d"),
                "count": count
            })
        
        return {
            "recent_activity": {
                "last_24h_detections": last_24h,
                "last_7d_detections": last_7d,
                "last_30d_detections": last_30d
            },
            "daily_pattern": daily_detections
        }
    
    def _generate_recommendations(self, sound_stats, category_stats, critical_sounds, temporal_patterns) -> List[str]:
        """Genera recomendaciones basadas en los datos del reporte"""
        recommendations = []
        
        # Recomendaciones basadas en sonidos críticos específicos
        if critical_sounds:
            critical_sound = critical_sounds[0]['sound_type']
            if 'sirena' in critical_sound.lower():
                recommendations.append(
                    "🚨 **¡Emergencia detectada!** Busca señales visuales de emergencia y sigue las indicaciones de evacuación."
                )
            elif 'alarma' in critical_sound.lower():
                recommendations.append(
                    "🚨 **¡Alarma activada!** Busca luces parpadeantes y sigue las rutas de evacuación marcadas."
                )
            else:
                recommendations.append(
                    f"🚨 **¡Sonido crítico detectado!** Mantén la calma y busca información visual sobre la situación."
                )
        
        # Recomendaciones basadas en el sonido más frecuente
        if sound_stats:
            most_frequent = sound_stats[0]
            if 'perro' in most_frequent['label'].lower():
                recommendations.append(
                    "🐕 **¡Perros cerca!** Mantén distancia y busca señales visuales del dueño antes de acercarte."
                )
            elif 'bocina' in most_frequent['label'].lower() or 'claxon' in most_frequent['label'].lower():
                recommendations.append(
                    "🚗 **¡Tráfico activo!** Usa siempre los cruces peatonales y espera las luces verdes."
                )
            elif 'timbre' in most_frequent['label'].lower():
                recommendations.append(
                    "🔔 **¡Timbre frecuente!** Considera instalar una luz parpadeante para saber cuándo llegan visitas."
                )
            elif most_frequent['count'] >= 3:
                recommendations.append(
                    f"🔊 **{most_frequent['label']} frecuente.** Busca patrones visuales para anticiparte a este sonido."
                )
            elif most_frequent['count'] == 1:
                recommendations.append(
                    "✅ **Entorno tranquilo.** Aprovecha para practicar lectura labial o lenguaje de señas."
                )
        
        # Recomendaciones basadas en actividad
        if temporal_patterns['recent_activity']['last_24h_detections'] > 10:
            recommendations.append(
                "📊 **Entorno muy activo.** Considera usar vibraciones en tu teléfono para alertas importantes."
            )
        elif temporal_patterns['recent_activity']['last_24h_detections'] == 0:
            recommendations.append(
                "🌙 **Entorno muy tranquilo.** Perfecto para practicar comunicación visual con familiares."
            )
        
        # Recomendaciones basadas en tipos de sonido específicos
        if sound_stats:
            vehicle_sounds = [s for s in sound_stats if any(word in s['label'].lower() for word in ['bocina', 'claxon', 'sirena', 'vehículo', 'coche', 'car'])]
            if vehicle_sounds:
                recommendations.append(
                    "🚗 **Zona de tráfico.** Siempre cruza con compañía o usa apps de asistencia para peatones."
                )
            
            alarm_sounds = [s for s in sound_stats if any(word in s['label'].lower() for word in ['alarma', 'emergencia', 'incendio', 'evacuación'])]
            if alarm_sounds:
                recommendations.append(
                    "🚨 **Zona con alarmas.** Aprende las señales visuales de emergencia de tu edificio."
                )
        
        # Recomendación general si no hay otras
        if not recommendations:
            recommendations.append(
                "✅ Tu entorno está bien controlado. ¡Sigue así!"
            )
        
        return recommendations
    
    def get_user_sound_summary(self, user_id: int) -> Dict[str, Any]:
        """Obtiene un resumen rápido de sonidos para un usuario específico"""
        try:
            user_sounds = DetectedSound.objects.filter(user_id=user_id)
            
            summary = {
                "total_detections": user_sounds.count(),
                "today_detections": user_sounds.filter(
                    timestamp__date=timezone.now().date()
                ).count(),
                "critical_detections": user_sounds.filter(
                    models.Q(sound_type__is_critical=True) | 
                    models.Q(category__is_critical=True)
                ).count(),
                "most_frequent_sound": user_sounds.values('sound_type__label').annotate(
                    count=Count('id')
                ).order_by('-count').first()
            }
            
            return summary
            
        except Exception as e:
            self.logger.error(f"Error obteniendo resumen de usuario {user_id}: {e}")
            return {"error": str(e)} 