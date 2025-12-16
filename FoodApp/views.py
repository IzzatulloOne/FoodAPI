from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.filters import SearchFilter, OrderingFilter
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework_simplejwt.tokens import RefreshToken

from .models import Food, Promocode, Buyurtma, BuyurtmaItems
from .serializers import (
    FoodSerializer,
    PromocodeSerializer,
    BuyurtmaSerializer,
    BuyurtmaItemInlineSerializer,
    RegisterSerializer
)
from .pagination import CustomPagination
from drf_spectacular.utils import extend_schema



class RegisterView(APIView):
    permission_classes = [AllowAny]

    @extend_schema(
        request=RegisterSerializer,
        responses={201: RegisterSerializer},
    )


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
                "phone": user.phone
            },
            "refresh": str(refresh),
            "access": str(refresh.access_token),
        }, status=status.HTTP_201_CREATED)


class FoodListCreateView(generics.ListCreateAPIView):
    queryset = Food.objects.all()
    serializer_class = FoodSerializer
    pagination_class = CustomPagination
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    search_fields = ['nomi', 'description']
    ordering_fields = ['narxi', 'created_at']
    ordering = ['-created_at']


class PromocodeListCreateView(generics.ListCreateAPIView):
    queryset = Promocode.objects.all()
    serializer_class = PromocodeSerializer
    pagination_class = CustomPagination
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    ordering_fields = ['start_date', 'end_date']
    ordering = ['-start_date']


class BuyurtmaListCreateView(generics.ListCreateAPIView):
    queryset = Buyurtma.objects.all()
    serializer_class = BuyurtmaSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = CustomPagination
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    search_fields = ['manzil']
    ordering_fields = ['created_at', 'total_price']
    ordering = ['-created_at']

    def perform_create(self, serializer):
        serializer.save(user_id=self.request.user)


class BuyurtmaItemsListCreateView(generics.ListCreateAPIView):
    queryset = BuyurtmaItems.objects.all()
    serializer_class = BuyurtmaItemInlineSerializer
    pagination_class = CustomPagination
    filter_backends = [DjangoFilterBackend]
