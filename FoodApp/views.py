from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAdminUser, BasePermission
from rest_framework.filters import SearchFilter, OrderingFilter
from django_filters.rest_framework import DjangoFilterBackend
from .models import Food, Promocode, Buyurtma, BuyurtmaItems
from .serializers import FoodSerializer,PromocodeSerializer,BuyurtmaSerializer,BuyurtmaItemsSerializer
from .pagination import CustomPagination
from django_filters import rest_framework as filters
from .models import Buyurtma



class BuyurtmaFilter(filters.FilterSet):
    status = filters.CharFilter(field_name='status')

    class Meta:
        model = Buyurtma
        fields = ['status']


class IsAdminOrReadOnly(BasePermission):
    def has_permission(self, request, view):
        if request.method in ['GET', 'HEAD', 'OPTIONS']:
            return True
        return request.user.is_authenticated and request.user.role


class FoodListCreateView(generics.ListCreateAPIView):
    queryset = Food.objects.all()
    serializer_class = FoodSerializer
    permission_classes = [IsAdminOrReadOnly]
    pagination_class = CustomPagination
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['narxi']
    search_fields = ['nomi', 'description']
    ordering_fields = ['narxi', 'created_at']
    ordering = ['-created_at']


class PromocodeListCreateView(generics.ListCreateAPIView):
    queryset = Promocode.objects.all()
    serializer_class = PromocodeSerializer
    permission_classes = [IsAdminUser]
    pagination_class = CustomPagination
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = ['nomi']
    ordering_fields = ['start_date', 'end_date']
    ordering = ['-start_date']


class BuyurtmaListCreateView(generics.ListCreateAPIView):
    serializer_class = BuyurtmaSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = CustomPagination
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = BuyurtmaFilter
    search_fields = ['manzil']
    ordering_fields = ['created_at', 'total_price']
    ordering = ['-created_at']

    def get_queryset(self):
        user = self.request.user
        if user.is_superuser or user.role:
            return Buyurtma.objects.all()
        return Buyurtma.objects.filter(user_id=user)


class BuyurtmaRetrieveUpdateView(generics.RetrieveUpdateAPIView):
    queryset = Buyurtma.objects.all()
    serializer_class = BuyurtmaSerializer
    permission_classes = [IsAuthenticated]

    def update(self, request, *args, **kwargs):
        buyurtma = self.get_object()

        if not request.user.role and buyurtma.user_id != request.user:
            return Response(
                {"detail": "Ruxsat yo‘q"},
                status=status.HTTP_403_FORBIDDEN
            )

        return super().update(request, *args, **kwargs)


class BuyurtmaItemsListCreateView(generics.ListCreateAPIView):
    serializer_class = BuyurtmaItemsSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = CustomPagination
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['buyurtma_id', 'food_id']

    def get_queryset(self):
        user = self.request.user
        if user.is_superuser or user.role:
            return BuyurtmaItems.objects.all()
        return BuyurtmaItems.objects.filter(buyurtma_id__user_id=user)