import os
import django
from django.core.asgi import get_asgi_application

# Use PyMySQL as a drop-in replacement for mysqlclient
try:
    import pymysql
    pymysql.install_as_MySQLdb()
except ImportError:
    pass

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'inventory_project.settings')
django.setup()

from channels.routing import ProtocolTypeRouter, URLRouter
import shop.routing

application = ProtocolTypeRouter({
    'http': get_asgi_application(),
    'websocket': URLRouter(shop.routing.websocket_urlpatterns),
})
