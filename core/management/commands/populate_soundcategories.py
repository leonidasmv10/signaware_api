from django.core.management.base import BaseCommand
from core.models import SoundCategory

CATEGORIES = [
    {"name": "danger_alert", "label": "Alerta de peligro", "emoji": "🔴"},
    {"name": "attention_alert", "label": "Atención requerida", "emoji": "🟡"},
    {"name": "social_alert", "label": "Actividad social", "emoji": "🟢"},
    {"name": "environment_alert", "label": "Cambio en el entorno", "emoji": "🔵"},
]

class Command(BaseCommand):
    help = 'Pobla la tabla SoundCategory con las categorías recomendadas.'

    def handle(self, *args, **options):
        for cat in CATEGORIES:
            obj, created = SoundCategory.objects.get_or_create(
                name=cat["name"],
                defaults={"label": cat["label"], "emoji": cat["emoji"]}
            )
            if created:
                self.stdout.write(self.style.SUCCESS(f"Creada: {obj}"))
            else:
                self.stdout.write(self.style.WARNING(f"Ya existía: {obj}")) 