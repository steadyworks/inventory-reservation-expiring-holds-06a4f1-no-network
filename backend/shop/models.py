from django.db import models
from django.utils import timezone

HOLD_DURATION_SECONDS = 90


class Product(models.Model):
    name = models.CharField(max_length=255)
    image_url = models.TextField(blank=True, default='')
    initial_stock = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        app_label = 'shop'

    def __str__(self):
        return self.name


class Hold(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='holds')
    user_name = models.CharField(max_length=255)
    expires_at = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        app_label = 'shop'
        unique_together = [['product', 'user_name']]

    @property
    def is_active(self):
        return self.expires_at > timezone.now()

    def __str__(self):
        return f'{self.user_name} holds {self.product.name}'


class Order(models.Model):
    user_name = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        app_label = 'shop'

    def __str__(self):
        return f'Order #{self.id} by {self.user_name}'


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)

    class Meta:
        app_label = 'shop'

    def __str__(self):
        return f'{self.product.name} in order #{self.order.id}'
