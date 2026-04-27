import asyncio
import json

from channels.generic.websocket import AsyncWebsocketConsumer

# Track connected channel names in memory (single-process only)
_connected_channels: set = set()
_cleanup_task = None
_cleanup_running = False


class InventoryConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        global _cleanup_task, _cleanup_running

        _connected_channels.add(self.channel_name)
        await self.channel_layer.group_add('inventory', self.channel_name)
        await self.accept()

        # Start background cleanup task if not already running
        if not _cleanup_running:
            _cleanup_running = True
            _cleanup_task = asyncio.ensure_future(self._periodic_cleanup())

        # Send current inventory state to this client
        from asgiref.sync import sync_to_async
        from shop.views import get_products_data

        products_data = await sync_to_async(get_products_data)()
        await self.send(text_data=json.dumps({
            'type': 'inventory_update',
            'products': products_data,
        }))

        # Broadcast updated user count
        await self.channel_layer.group_send('inventory', {
            'type': 'user_count_update',
            'count': len(_connected_channels),
        })

    async def disconnect(self, close_code):
        _connected_channels.discard(self.channel_name)
        await self.channel_layer.group_discard('inventory', self.channel_name)

        # Broadcast updated user count
        await self.channel_layer.group_send('inventory', {
            'type': 'user_count_update',
            'count': len(_connected_channels),
        })

    async def receive(self, text_data):
        pass  # No client-to-server messages needed

    async def inventory_update(self, event):
        await self.send(text_data=json.dumps({
            'type': 'inventory_update',
            'products': event['products'],
        }))

    async def user_count_update(self, event):
        await self.send(text_data=json.dumps({
            'type': 'user_count_update',
            'count': event['count'],
        }))

    @staticmethod
    async def _periodic_cleanup():
        """Background task: clean expired holds and broadcast every 5 seconds."""
        global _cleanup_running

        from asgiref.sync import sync_to_async
        from channels.layers import get_channel_layer
        from django.utils import timezone

        from shop.models import Hold
        from shop.views import get_products_data

        channel_layer = get_channel_layer()

        try:
            while _cleanup_running:
                await asyncio.sleep(1)
                now = timezone.now()

                expired_count = await sync_to_async(
                    lambda: Hold.objects.filter(expires_at__lte=now).count()
                )()

                if expired_count > 0:
                    await sync_to_async(
                        lambda: Hold.objects.filter(expires_at__lte=timezone.now()).delete()
                    )()

                    products_data = await sync_to_async(get_products_data)()
                    await channel_layer.group_send('inventory', {
                        'type': 'inventory_update',
                        'products': products_data,
                    })
        except asyncio.CancelledError:
            pass
        finally:
            _cleanup_running = False
