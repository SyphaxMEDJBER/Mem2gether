"""Point d'entree ASGI.

ASGI sert a la fois les requetes HTTP Django classiques et les connexions
WebSocket Django Channels utilisees par les rooms.
"""

import os

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "application.settings")

import django
django.setup()

from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
import application.routing
import rooms.routing
application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    "websocket": AuthMiddlewareStack(
        URLRouter(
            application.routing.websocket_urlpatterns
            + rooms.routing.websocket_urlpatterns
        )
    ),
})
