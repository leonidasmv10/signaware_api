import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'signaware_api.settings')
django.setup()  # Configura Django antes de importar módulos que dependan de él

from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
from channels.security.websocket import AllowedHostsOriginValidator

# Importa routing DESPUÉS de configurar Django
import models_ai.routing

application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    "websocket": AllowedHostsOriginValidator(
        AuthMiddlewareStack(
            URLRouter(
                models_ai.routing.websocket_urlpatterns
            )
        )
    ),
})