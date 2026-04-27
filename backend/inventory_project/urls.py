from django.urls import path
from shop.views import (
    ProductListView,
    ResetView,
    HoldView,
    HoldReleaseView,
    CheckoutView,
    OrderView,
    UserHoldsView,
)

urlpatterns = [
    path('api/products/', ProductListView.as_view()),
    path('api/reset/', ResetView.as_view()),
    path('api/holds/', HoldView.as_view()),
    path('api/holds/<int:product_id>/', HoldReleaseView.as_view()),
    path('api/checkout/', CheckoutView.as_view()),
    path('api/orders/', OrderView.as_view()),
    path('api/user-holds/', UserHoldsView.as_view()),
]
