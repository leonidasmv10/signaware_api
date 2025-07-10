from django.core.management.base import BaseCommand
from core.models import SoundType

class Command(BaseCommand):
    help = 'Pobla la base de datos con tipos de sonidos por defecto'

    def handle(self, *args, **options):
        def normalize_name(name):
            return name.strip().lower().replace(' ', '_')

        sound_types = [
            # Alarmas y alertas de peligro
            {
                'name': 'alarm',
                'label': 'Alarma',
                'description': 'Alarmas generales',
                'is_critical': True
            },
            {
                'name': 'fire_alarm',
                'label': 'Alarma de Incendio',
                'description': 'Alarmas de incendio y detectores de humo',
                'is_critical': True
            },
            {
                'name': 'smoke_detector',
                'label': 'Detector de Humo',
                'description': 'Detectores de humo',
                'is_critical': True
            },
            {
                'name': 'siren',
                'label': 'Sirena',
                'description': 'Sirenas de emergencia (policía, ambulancia, bomberos)',
                'is_critical': True
            },
            {
                'name': 'civil_defense_siren',
                'label': 'Sirena de Defensa Civil',
                'description': 'Sirenas de defensa civil',
                'is_critical': True
            },
            {
                'name': 'telephone_bell',
                'label': 'Timbre de Teléfono',
                'description': 'Timbres de teléfono',
                'is_critical': False
            },
            {
                'name': 'ringtone',
                'label': 'Tono de Llamada',
                'description': 'Tonos de llamada de móviles',
                'is_critical': False
            },
            {
                'name': 'doorbell',
                'label': 'Timbre de Puerta',
                'description': 'Timbres de puerta',
                'is_critical': False
            },
            {
                'name': 'ding_dong',
                'label': 'Ding-Dong',
                'description': 'Sonidos de timbre ding-dong',
                'is_critical': False
            },
            {
                'name': 'whistle',
                'label': 'Silbato',
                'description': 'Silbatos',
                'is_critical': False
            },
            
            # Sonidos sociales y humanos
            {
                'name': 'shout',
                'label': 'Grito',
                'description': 'Gritos y voces elevadas',
                'is_critical': True
            },
            {
                'name': 'yell',
                'label': 'Aullido',
                'description': 'Aullidos y voces muy altas',
                'is_critical': True
            },
            {
                'name': 'children_shouting',
                'label': 'Niños Gritando',
                'description': 'Gritos de niños',
                'is_critical': False
            },
            {
                'name': 'screaming',
                'label': 'Grito de Pánico',
                'description': 'Gritos de pánico o miedo',
                'is_critical': True
            },
            {
                'name': 'speech',
                'label': 'Conversación',
                'description': 'Voz humana y conversaciones',
                'is_critical': False
            },
            {
                'name': 'child_speech',
                'label': 'Voz de Niño',
                'description': 'Voz de niños hablando',
                'is_critical': False
            },
            {
                'name': 'conversation',
                'label': 'Conversación',
                'description': 'Conversaciones entre personas',
                'is_critical': False
            },
            {
                'name': 'crying',
                'label': 'Llanto',
                'description': 'Llanto de personas',
                'is_critical': False
            },
            {
                'name': 'baby_cry',
                'label': 'Llanto de Bebé',
                'description': 'Llanto de bebés',
                'is_critical': False
            },
            {
                'name': 'laughter',
                'label': 'Risa',
                'description': 'Risas de personas',
                'is_critical': False
            },
            {
                'name': 'baby_laughter',
                'label': 'Risa de Bebé',
                'description': 'Risas de bebés',
                'is_critical': False
            },
            {
                'name': 'giggle',
                'label': 'Risita',
                'description': 'Risitas y risas suaves',
                'is_critical': False
            },
            
            # Sonidos de movimiento y ambiente
            {
                'name': 'run',
                'label': 'Correr',
                'description': 'Sonidos de personas corriendo',
                'is_critical': False
            },
            {
                'name': 'footsteps',
                'label': 'Pasos',
                'description': 'Sonidos de pasos',
                'is_critical': False
            },
            
            # Sonidos de vehículos
            {
                'name': 'vehicle_horn',
                'label': 'Bocina de Vehículo',
                'description': 'Bocinas de vehículos',
                'is_critical': True
            },
            {
                'name': 'car_alarm',
                'label': 'Alarma de Auto',
                'description': 'Alarmas de automóviles',
                'is_critical': True
            },
            {
                'name': 'reversing_beeps',
                'label': 'Beeps de Reversa',
                'description': 'Sonidos de reversa de vehículos',
                'is_critical': False
            },
            {
                'name': 'train',
                'label': 'Tren',
                'description': 'Sonidos de trenes',
                'is_critical': False
            },
            {
                'name': 'subway',
                'label': 'Metro',
                'description': 'Sonidos de metro/subterráneo',
                'is_critical': False
            },
            {
                'name': 'car_passing',
                'label': 'Auto Pasando',
                'description': 'Autos pasando cerca',
                'is_critical': False
            },
            
            # Sonidos de animales
            {
                'name': 'dog',
                'label': 'Perro',
                'description': 'Sonidos de perros',
                'is_critical': False
            },
            {
                'name': 'bark',
                'label': 'Ladrido',
                'description': 'Ladridos de perros',
                'is_critical': False
            },
            {
                'name': 'whimper_dog',
                'label': 'Gemido de Perro',
                'description': 'Gemidos de perros',
                'is_critical': False
            },
            
            # Sonidos de objetos
            {
                'name': 'glass',
                'label': 'Vidrio',
                'description': 'Sonidos relacionados con vidrio',
                'is_critical': False
            },
            {
                'name': 'shatter',
                'label': 'Estallido',
                'description': 'Sonidos de objetos rompiéndose',
                'is_critical': True
            },
            {
                'name': 'door',
                'label': 'Puerta',
                'description': 'Sonidos de puertas',
                'is_critical': False
            },
            {
                'name': 'slam',
                'label': 'Portazo',
                'description': 'Sonidos de puertas cerrándose fuerte',
                'is_critical': False
            },
            {
                'name': 'knock',
                'label': 'Golpe',
                'description': 'Golpes en puertas',
                'is_critical': False
            },
            
            # Sonidos domésticos
            {
                'name': 'toilet_flush',
                'label': 'Descarga de Baño',
                'description': 'Sonido de descarga de inodoro',
                'is_critical': False
            },
            {
                'name': 'frying_food',
                'label': 'Freír Comida',
                'description': 'Sonidos de freír comida',
                'is_critical': False
            },
            {
                'name': 'water_tap',
                'label': 'Grifo de Agua',
                'description': 'Sonidos de grifos de agua',
                'is_critical': False
            },
            
            # Sonidos de fuego y naturaleza
            {
                'name': 'fire',
                'label': 'Fuego',
                'description': 'Sonidos de fuego',
                'is_critical': True
            },
            {
                'name': 'crackle',
                'label': 'Crujido',
                'description': 'Sonidos de crujidos (fuego, etc.)',
                'is_critical': False
            },
            
            # Sonidos sociales
            {
                'name': 'children_playing',
                'label': 'Niños Jugando',
                'description': 'Sonidos de niños jugando',
                'is_critical': False
            },
            {
                'name': 'applause',
                'label': 'Aplausos',
                'description': 'Sonidos de aplausos',
                'is_critical': False
            },
            {
                'name': 'crowd',
                'label': 'Multitud',
                'description': 'Sonidos de multitudes',
                'is_critical': False
            },
            
            # Sonidos naturales
            {
                'name': 'thunder',
                'label': 'Trueno',
                'description': 'Sonidos de truenos',
                'is_critical': False
            },
            {
                'name': 'rain',
                'label': 'Lluvia',
                'description': 'Sonidos de lluvia',
                'is_critical': False
            },
            {
                'name': 'rain_on_surface',
                'label': 'Lluvia en Superficie',
                'description': 'Sonidos de lluvia golpeando superficies',
                'is_critical': False
            },
            
            # Sonidos adicionales importantes
            {
                'name': 'gun_shot',
                'label': 'Disparo',
                'description': 'Sonidos de armas de fuego',
                'is_critical': True
            },
            {
                'name': 'glass_breaking',
                'label': 'Vidrio Roto',
                'description': 'Sonido de vidrios rompiéndose',
                'is_critical': True
            },
            {
                'name': 'music',
                'label': 'Música',
                'description': 'Música y sonidos musicales',
                'is_critical': False
            },
            {
                'name': 'traffic',
                'label': 'Tráfico',
                'description': 'Sonidos de tráfico vehicular',
                'is_critical': False
            },
            {
                'name': 'construction',
                'label': 'Construcción',
                'description': 'Sonidos de construcción y obras',
                'is_critical': False
            },
            {
                'name': 'nature',
                'label': 'Naturaleza',
                'description': 'Sonidos naturales (aves, viento, etc.)',
                'is_critical': False
            },
            {
                'name': 'appliance',
                'label': 'Electrodomésticos',
                'description': 'Sonidos de electrodomésticos',
                'is_critical': False
            }
        ]

        # Normaliza los nombres de la lista
        normalized_names = set(normalize_name(st['name']) for st in sound_types)

        # Elimina duplicados y tipos no deseados
        deleted, _ = SoundType.objects.exclude(name__in=normalized_names).delete()
        self.stdout.write(self.style.WARNING(f'Eliminados {deleted} tipos de sonido no deseados o duplicados.'))

        created_count = 0
        updated_count = 0
        for sound_type_data in sound_types:
            normalized_name = normalize_name(sound_type_data['name'])
            obj, created = SoundType.objects.update_or_create(
                name=normalized_name,
                defaults={
                    'label': sound_type_data['label'],
                    'description': sound_type_data['description'],
                    'is_critical': sound_type_data['is_critical']
                }
            )
            if created:
                created_count += 1
                self.stdout.write(self.style.SUCCESS(f'Creado: {obj.label}'))
            else:
                updated_count += 1
                self.stdout.write(self.style.WARNING(f'Actualizado: {obj.label}'))

        self.stdout.write(self.style.SUCCESS(f'Proceso completado. {created_count} tipos de sonido creados, {updated_count} actualizados.')) 