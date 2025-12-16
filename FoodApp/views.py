from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAdminUser, BasePermission, AllowAny
from rest_framework.filters import SearchFilter, OrderingFilter
from django_filters.rest_framework import DjangoFilterBackend
from django_filters import rest_framework as filters
from .models import Food, Promocode, Buyurtma, BuyurtmaItems
from .serializers import (
    FoodSerializer, PromocodeSerializer, BuyurtmaItemsSerializer, BuyurtmaItemsSerializer,
    RegisterSerializer
)
from .pagination import CustomPagination
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from drf_yasg.utils import swagger_auto_schema


class IsAdminOrReadOnly(BasePermission):
    def has_permission(self, request, view):
        if request.method in ['GET', 'HEAD', 'OPTIONS']:
            return True
        user = request.user
        if not user or not user.is_authenticated:
            return False
        if user.is_superuser:
            return True
        return getattr(user, 'role', False)


class RegisterView(APIView):
    permission_classes = [AllowAny]

    @swagger_auto_schema(tags=["AUTH"])
    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        refresh = RefreshToken.for_user(user)
        return Response({
            "user": {
                "id": user.id,
                "username": user.username,
                "email": user.email,
            },
            "refresh": str(refresh),
            "access": str(refresh.access_token),
        }, status=status.HTTP_201_CREATED)


class BuyurtmaFilter(filters.FilterSet):
    status = filters.CharFilter(field_name='status')

    class Meta:
        model = Buyurtma
        fields = ['status']


class BuyurtmaItemsFilter(filters.FilterSet):
    class Meta:
        model = BuyurtmaItems
        fields = ['buyurtma_id', 'food_id']


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

    @swagger_auto_schema(tags=["FOODS"])
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    @swagger_auto_schema(tags=["FOODS"])
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)


class PromocodeListCreateView(generics.ListCreateAPIView):
    queryset = Promocode.objects.all()
    serializer_class = PromocodeSerializer
    permission_classes = [IsAdminUser]
    pagination_class = CustomPagination
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = ['nomi']
    ordering_fields = ['start_date', 'end_date']
    ordering = ['-start_date']

    @swagger_auto_schema(tags=["PROMOCODES"])
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    @swagger_auto_schema(tags=["PROMOCODES"])
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)


class BuyurtmaListCreateView(generics.ListCreateAPIView):
    serializer_class = BuyurtmaItemsSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = CustomPagination
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = BuyurtmaFilter
    search_fields = ['manzil']
    ordering_fields = ['created_at', 'total_price']
    ordering = ['-created_at']

    @swagger_auto_schema(tags=["ORDERS"])
    def get_queryset(self):
        user = self.request.user
        if user.is_superuser or getattr(user, 'role', False):
            return Buyurtma.objects.all()
        return Buyurtma.objects.filter(user=user)

    @swagger_auto_schema(tags=["ORDERS"])
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class BuyurtmaItemsListCreateView(generics.ListCreateAPIView):
    serializer_class = BuyurtmaItemsSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = CustomPagination
    filter_backends = [DjangoFilterBackend]
    filterset_class = BuyurtmaItemsFilter

    @swagger_auto_schema(tags=["ORDERS"])
    def get_queryset(self):
        user = self.request.user
        if user.is_superuser or getattr(user, 'role', False):
            return BuyurtmaItems.objects.all()
        return BuyurtmaItems.objects.filter(buyurtma__user=user)

    @swagger_auto_schema(tags=["ORDERS"])
    def perform_create(self, serializer):
        serializer.save()
