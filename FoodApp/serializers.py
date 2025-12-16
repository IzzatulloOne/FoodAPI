from rest_framework.serializers import ModelSerializer
from rest_framework import serializers
from .models import Food, Promocode, Buyurtma, BuyurtmaItems, CustomUser
from .models import CustomUser



class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = CustomUser
        fields = ['id', 'username', 'email', 'phone', 'password']

    def create(self, validated_data):
        password = validated_data.pop('password')
        user = CustomUser(**validated_data)
        user.set_password(password)
        user.save()
        return user


class CustomUserSerializer(ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = CustomUser
        fields = '__all__'
        read_only_fields = ['id', 'created_at']

    def create(self, validated_data):
        password = validated_data.pop('password')
        user = CustomUser(**validated_data)
        user.set_password(password)
        user.save()
        return user


class FoodSerializer(ModelSerializer):
    class Meta:
        model = Food
        fields = '__all__'
        read_only_fields = ['id', 'created_at']


class PromocodeSerializer(ModelSerializer):
    class Meta:
        model = Promocode
        fields = '__all__'
        read_only_fields = ['id']


class BuyurtmaItemsSerializer(serializers.ModelSerializer):
    food = serializers.PrimaryKeyRelatedField(
        source='food_id',
        queryset=Food.objects.all()
    )
    class Meta:
        model = BuyurtmaItems
        fields = ['food', 'count']


class BuyurtmaSerializer(serializers.ModelSerializer):
    items = BuyurtmaItemsSerializer(many=True, write_only=True)
    promocode = serializers.PrimaryKeyRelatedField(
        source='promocode_id',
        queryset=Promocode.objects.all(),
        required=False,
        allow_null=True
    )

    class Meta:
        model = Buyurtma
        fields = ['id','user_id','manzil','items','total_price','promocode','promocode_applied','status','created_at']
        read_only_fields = ['id', 'total_price', 'created_at', 'status']

    def create(self, validated_data):
        items_data = validated_data.pop('items', None)

        if not items_data:
            raise serializers.ValidationError({
                "items": "Buyurtma yaratishda mahsulotlar bo‘lishi shart"
            })

        promocode = validated_data.get('promocode_id')

        buyurtma = Buyurtma.objects.create(**validated_data)

        total = 0

        for item in items_data:
            food = item['food_id']
            count = item['count']

            item_total = food.narxi * count

            BuyurtmaItems.objects.create(
                buyurtma_id=buyurtma,
                food_id=food,
                count=count,
                total_price=item_total
            )

            total += item_total

        discount = 0
        if promocode and promocode.is_active():
            discount = min(promocode.discount_amount, promocode.max_discount)
            promocode.used_count += 1
            promocode.save()
            buyurtma.promocode_applied = True

        buyurtma.total_price = max(total - discount, 0)
        buyurtma.save()

        return buyurtma
