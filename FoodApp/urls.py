from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from .views import FoodListCreateView, PromocodeListCreateView, BuyurtmaListCreateView, BuyurtmaItemsListCreateView


urlpatterns = [
    path('foods/', FoodListCreateView.as_view(), name='foods-list'),
    path('promocodes/', PromocodeListCreateView.as_view(), name='promocodes-list'),
    path('buyurtma/', BuyurtmaListCreateView.as_view(), name='buyurtma-list'),
    path('buyurtma-items/', BuyurtmaItemsListCreateView.as_view(), name='buyurtma-items-list'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)