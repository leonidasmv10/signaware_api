"""
Comando de Django para actualizar la base de datos de audífonos.
Ejecutar: python manage.py update_hearing_aids_db
"""

import asyncio
import logging
from django.core.management.base import BaseCommand
from agent.services.rag_service import RagService


class Command(BaseCommand):
    help = 'Actualiza la base de datos de audífonos con web scraping en tiempo real'

    def add_arguments(self, parser):
        parser.add_argument(
            '--brand',
            type=str,
            default='phonak',
            help='Marca de audífonos a scrapear (default: phonak)'
        )
        parser.add_argument(
            '--force',
            action='store_true',
            help='Forzar actualización completa'
        )
        parser.add_argument(
            '--stats',
            action='store_true',
            help='Mostrar estadísticas de la base de datos'
        )

    def handle(self, *args, **options):
        # Configurar logging
        logging.basicConfig(level=logging.INFO)
        logger = logging.getLogger(__name__)
        
        rag_service = RagService()
        
        if options['stats']:
            # Mostrar estadísticas
            stats = rag_service.get_database_stats()
            if 'error' in stats:
                self.stdout.write(
                    self.style.ERROR(f"❌ Error obteniendo estadísticas: {stats['error']}")
                )
            else:
                self.stdout.write(
                    self.style.SUCCESS("📊 Estadísticas de la Base de Datos:")
                )
                self.stdout.write(f"   Total audífonos: {stats['total_audifonos']}")
                self.stdout.write(f"   Marcas: {stats['marcas']}")
                self.stdout.write(f"   Tecnologías populares: {stats['tecnologias_populares']}")
                self.stdout.write(f"   Última actualización: {stats['ultima_actualizacion']}")
            return
        
        # Actualizar base de datos
        brand = options['brand']
        force = options['force']
        
        self.stdout.write(
            self.style.SUCCESS(f"🔄 Iniciando actualización de base de datos para marca: {brand}")
        )
        
        if force:
            self.stdout.write("⚠️  Modo forzado activado - actualización completa")
        
        try:
            # Ejecutar actualización asíncrona
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            result = loop.run_until_complete(
                rag_service.update_hearing_aids_database()
            )
            
            if result['success']:
                self.stdout.write(
                    self.style.SUCCESS(f"✅ Actualización completada exitosamente!")
                )
                self.stdout.write(f"   Audífonos procesados: {result['audifonos_procesados']}")
                self.stdout.write(f"   Fecha: {result['fecha_actualizacion']}")
            else:
                self.stdout.write(
                    self.style.ERROR(f"❌ Error en actualización: {result['message']}")
                )
                
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f"❌ Error ejecutando actualización: {e}")
            )
        finally:
            loop.close() 