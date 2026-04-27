import json
from datetime import timedelta

from django.db import transaction
from django.http import JsonResponse
from django.utils import timezone
from django.views import View

from .models import HOLD_DURATION_SECONDS, Hold, Order, OrderItem, Product


def get_available_qty(product, now=None):
    if now is None:
        now = timezone.now()
    active_holds_count = Hold.objects.filter(
        product=product,
        expires_at__gt=now
    ).count()
    confirmed_orders_count = OrderItem.objects.filter(product=product).count()
    return product.initial_stock - active_holds_count - confirmed_orders_count


def get_products_data():
    now = timezone.now()
    products = Product.objects.all().order_by('created_at')
    result = []
    for p in products:
        active_holds_count = Hold.objects.filter(product=p, expires_at__gt=now).count()
        confirmed_orders_count = OrderItem.objects.filter(product=p).count()
        available = p.initial_stock - active_holds_count - confirmed_orders_count
        result.append({
            'id': p.id,
            'name': p.name,
            'image_url': p.image_url,
            'initial_stock': p.initial_stock,
            'available_qty': available,
        })
    return result


def broadcast_update():
    from channels.layers import get_channel_layer
    from asgiref.sync import async_to_sync

    channel_layer = get_channel_layer()
    products_data = get_products_data()
    async_to_sync(channel_layer.group_send)(
        'inventory',
        {
            'type': 'inventory_update',
            'products': products_data,
        }
    )


class ProductListView(View):
    def get(self, request):
        products_data = get_products_data()
        return JsonResponse({'products': products_data})

    def post(self, request):
        try:
            data = json.loads(request.body)
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON'}, status=400)

        name = data.get('name', '').strip()
        if not name:
            return JsonResponse({'error': 'Name is required'}, status=400)

        try:
            initial_stock = int(data.get('initial_stock', 0))
            if initial_stock <= 0:
                raise ValueError
        except (ValueError, TypeError):
            return JsonResponse({'error': 'Stock must be a positive integer'}, status=400)

        product = Product.objects.create(
            name=name,
            image_url=data.get('image_url', '') or '',
            initial_stock=initial_stock,
        )
        broadcast_update()
        return JsonResponse({
            'id': product.id,
            'name': product.name,
            'image_url': product.image_url,
            'initial_stock': product.initial_stock,
            'available_qty': product.initial_stock,
        }, status=201)


class ResetView(View):
    def post(self, request):
        Hold.objects.all().delete()
        OrderItem.objects.all().delete()
        Order.objects.all().delete()
        Product.objects.all().delete()
        broadcast_update()
        return JsonResponse({'status': 'ok'})


class HoldView(View):
    def post(self, request):
        try:
            data = json.loads(request.body)
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON'}, status=400)

        user_name = data.get('user_name', '').strip()
        product_id = data.get('product_id')

        if not user_name or not product_id:
            return JsonResponse({'error': 'user_name and product_id required'}, status=400)

        with transaction.atomic():
            now = timezone.now()

            # Clean up expired holds first
            Hold.objects.filter(expires_at__lte=now).delete()

            # Check 3-item hold limit for this user
            active_holds_count = Hold.objects.filter(
                user_name=user_name,
                expires_at__gt=now
            ).count()
            if active_holds_count >= 3:
                return JsonResponse(
                    {'error': 'You can hold at most 3 items at a time'},
                    status=400
                )

            # Check if user already holds this product
            existing = Hold.objects.filter(
                user_name=user_name,
                product_id=product_id,
                expires_at__gt=now
            ).first()
            if existing:
                return JsonResponse({'error': 'You already hold this item'}, status=400)

            # Lock the product row to prevent concurrent over-reservation
            try:
                product = Product.objects.select_for_update().get(id=product_id)
            except Product.DoesNotExist:
                return JsonResponse({'error': 'Product not found'}, status=404)

            available = get_available_qty(product, now)
            if available <= 0:
                return JsonResponse({'error': 'Out of stock'}, status=400)

            expires_at = now + timedelta(seconds=HOLD_DURATION_SECONDS)
            hold = Hold.objects.create(
                product=product,
                user_name=user_name,
                expires_at=expires_at,
            )

        broadcast_update()
        return JsonResponse({
            'id': hold.id,
            'product_id': product_id,
            'expires_at': hold.expires_at.isoformat(),
            'seconds_remaining': HOLD_DURATION_SECONDS,
        }, status=201)


class HoldReleaseView(View):
    def delete(self, request, product_id):
        user_name = request.GET.get('user_name', '').strip()
        if not user_name:
            return JsonResponse({'error': 'user_name required'}, status=400)

        Hold.objects.filter(
            product_id=product_id,
            user_name=user_name,
            expires_at__gt=timezone.now()
        ).delete()

        broadcast_update()
        return JsonResponse({'status': 'ok'})


class CheckoutView(View):
    def post(self, request):
        try:
            data = json.loads(request.body)
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON'}, status=400)

        user_name = data.get('user_name', '').strip()
        if not user_name:
            return JsonResponse({'error': 'user_name required'}, status=400)

        with transaction.atomic():
            now = timezone.now()
            active_holds = list(
                Hold.objects.filter(
                    user_name=user_name,
                    expires_at__gt=now
                ).select_related('product')
            )

            if not active_holds:
                return JsonResponse({'error': 'No active holds to checkout'}, status=400)

            order = Order.objects.create(user_name=user_name)
            for hold in active_holds:
                OrderItem.objects.create(order=order, product=hold.product)

            Hold.objects.filter(id__in=[h.id for h in active_holds]).delete()

        broadcast_update()
        return JsonResponse({'order_id': order.id})


class OrderView(View):
    def get(self, request):
        user_name = request.GET.get('user_name', '').strip()
        if not user_name:
            return JsonResponse({'orders': []})

        orders = (
            Order.objects
            .filter(user_name=user_name)
            .prefetch_related('items__product')
            .order_by('created_at')
        )
        result = []
        for order in orders:
            result.append({
                'id': order.id,
                'created_at': order.created_at.isoformat(),
                'items': [
                    {
                        'product_id': item.product.id,
                        'product_name': item.product.name,
                    }
                    for item in order.items.all()
                ],
            })
        return JsonResponse({'orders': result})


class UserHoldsView(View):
    def get(self, request):
        user_name = request.GET.get('user_name', '').strip()
        if not user_name:
            return JsonResponse({'holds': []})

        now = timezone.now()
        holds = (
            Hold.objects
            .filter(user_name=user_name, expires_at__gt=now)
            .select_related('product')
        )
        result = []
        for hold in holds:
            seconds_remaining = max(0, int((hold.expires_at - now).total_seconds()))
            result.append({
                'product_id': hold.product.id,
                'product_name': hold.product.name,
                'expires_at': hold.expires_at.isoformat(),
                'seconds_remaining': seconds_remaining,
            })
        return JsonResponse({'holds': result})
