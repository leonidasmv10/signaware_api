#!/usr/bin/env python3
"""
Script para poblar la base de datos con datos de prueba para reportes de sonidos.
"""

import sys
import os
import django
from datetime import datetime, timedelta
import random

# Configurar Django
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'signaware_api.settings')
django.setup()

from django.utils import timezone
from agent.models import DetectedSound
from core.models import SoundCategory, SoundType
from django.contrib.auth import get_user_model
from django.db import models
from django.db.models import Count

User = get_user_model()


def create_test_data():
    """Crea datos de prueba para los reportes de sonidos."""
    
    print("🔧 Creando datos de prueba para reportes de sonidos...")
    
    # Crear categorías de sonidos si no existen
    categories = {
        'emergency': {'name': 'emergency', 'label': 'Emergencia', 'emoji': '🚨', 'is_critical': True},
        'vehicle': {'name': 'vehicle', 'label': 'Vehículos', 'emoji': '🚗', 'is_critical': False},
        'speech': {'name': 'speech', 'label': 'Habla', 'emoji': '🗣️', 'is_critical': False},
        'music': {'name': 'music', 'label': 'Música', 'emoji': '🎵', 'is_critical': False},
        'nature': {'name': 'nature', 'label': 'Naturaleza', 'emoji': '🌿', 'is_critical': False},
        'alarm': {'name': 'alarm', 'label': 'Alarmas', 'emoji': '⚠️', 'is_critical': True},
    }
    
    for cat_name, cat_data in categories.items():
        category, created = SoundCategory.objects.get_or_create(
            name=cat_data['name'],
            defaults=cat_data
        )
        if created:
            print(f"✅ Categoría creada: {category.label}")
    
    # Crear tipos de sonidos si no existen
    sound_types = {
        'siren': {'name': 'siren', 'label': 'Sirena', 'is_critical': True},
        'car_horn': {'name': 'car_horn', 'label': 'Bocina de Carro', 'is_critical': False},
        'speech': {'name': 'speech', 'label': 'Habla Humana', 'is_critical': False},
        'music': {'name': 'music', 'label': 'Música', 'is_critical': False},
        'alarm': {'name': 'alarm', 'label': 'Alarma', 'is_critical': True},
        'bird': {'name': 'bird', 'label': 'Pájaros', 'is_critical': False},
        'traffic': {'name': 'traffic', 'label': 'Tráfico', 'is_critical': False},
        'phone': {'name': 'phone', 'label': 'Teléfono', 'is_critical': False},
    }
    
    for sound_name, sound_data in sound_types.items():
        sound_type, created = SoundType.objects.get_or_create(
            name=sound_data['name'],
            defaults=sound_data
        )
        if created:
            print(f"✅ Tipo de sonido creado: {sound_type.label}")
    
    # Obtener o crear usuario de prueba
    user, created = User.objects.get_or_create(
        username='test_user',
        defaults={
            'email': 'test@example.com',
            'first_name': 'Test',
            'last_name': 'User'
        }
    )
    if created:
        print(f"✅ Usuario de prueba creado: {user.username}")
    
    # Crear detecciones de sonidos de prueba
    print("📊 Creando detecciones de sonidos de prueba...")
    
    # Obtener categorías y tipos
    categories = list(SoundCategory.objects.all())
    sound_types = list(SoundType.objects.all())
    
    # Generar detecciones en los últimos 30 días
    end_date = timezone.now()
    start_date = end_date - timedelta(days=30)
    
    detections_created = 0
    
    for i in range(100):  # Crear 100 detecciones
        # Fecha aleatoria en los últimos 30 días
        random_days = random.randint(0, 30)
        random_hours = random.randint(0, 23)
        random_minutes = random.randint(0, 59)
        
        timestamp = end_date - timedelta(
            days=random_days,
            hours=random_hours,
            minutes=random_minutes
        )
        
        # Seleccionar categoría y tipo aleatorios
        category = random.choice(categories)
        sound_type = random.choice(sound_types)
        
        # Confianza aleatoria entre 0.5 y 1.0
        confidence = round(random.uniform(0.5, 1.0), 3)
        
        # Crear detección
        detection = DetectedSound.objects.create(
            user=user,
            sound_type=sound_type,
            category=category,
            confidence=confidence,
            timestamp=timestamp,
            transcription=f"Transcripción de prueba {i+1}" if random.random() > 0.5 else ""
        )
        
        detections_created += 1
        
        if detections_created % 20 == 0:
            print(f"📈 Creadas {detections_created} detecciones...")
    
    print(f"✅ Se crearon {detections_created} detecciones de sonidos de prueba")
    print("🎯 Los datos de prueba están listos para generar reportes")


def show_test_data_summary():
    """Muestra un resumen de los datos de prueba creados."""
    
    print("\n📊 Resumen de datos de prueba:")
    print("=" * 40)
    
    # Estadísticas generales
    total_detections = DetectedSound.objects.count()
    total_categories = SoundCategory.objects.count()
    total_sound_types = SoundType.objects.count()
    
    print(f"• Total de detecciones: {total_detections}")
    print(f"• Categorías de sonidos: {total_categories}")
    print(f"• Tipos de sonidos: {total_sound_types}")
    
    # Detecciones por categoría
    print("\n🏷️ Detecciones por categoría:")
    category_stats = DetectedSound.objects.values('category__label').annotate(
        count=Count('id')
    ).order_by('-count')
    
    for stat in category_stats:
        print(f"  • {stat['category__label']}: {stat['count']}")
    
    # Detecciones por tipo
    print("\n🔊 Detecciones por tipo de sonido:")
    sound_stats = DetectedSound.objects.values('sound_type__label').annotate(
        count=Count('id')
    ).order_by('-count')
    
    for stat in sound_stats:
        print(f"  • {stat['sound_type__label']}: {stat['count']}")
    
    # Sonidos críticos
    critical_count = DetectedSound.objects.filter(
        models.Q(sound_type__is_critical=True) | 
        models.Q(category__is_critical=True)
    ).count()
    
    print(f"\n🚨 Sonidos críticos detectados: {critical_count}")
    
    # Últimas 24 horas
    last_24h = DetectedSound.objects.filter(
        timestamp__gte=timezone.now() - timedelta(hours=24)
    ).count()
    
    print(f"⏰ Detecciones en las últimas 24 horas: {last_24h}")


if __name__ == "__main__":
    try:
        create_test_data()
        show_test_data_summary()
        print("\n✅ Datos de prueba creados exitosamente")
        print("🎯 Ahora puedes probar los reportes de sonidos")
        
    except Exception as e:
        print(f"❌ Error creando datos de prueba: {e}")
        import traceback
        traceback.print_exc() 