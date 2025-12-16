from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import Food, Promocode, Buyurtma, BuyurtmaItems

User = get_user_model()


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'phone', 'password']

    def create(self, validated_data):
        password = validated_data.pop('password')
        user = User(**validated_data)
        user.set_password(password)
        user.save()
        return user


class FoodSerializer(serializers.ModelSerializer):
    class Meta:
        model = Food
        fields = '__all__'


class PromocodeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Promocode
        fields = '__all__'


class BuyurtmaItemInlineSerializer(serializers.ModelSerializer):
    food_id = serializers.PrimaryKeyRelatedField(
        queryset=Food.objects.all()
    )

    class Meta:
        model = BuyurtmaItems
        fields = ['food_id', 'count']


class BuyurtmaItemReadSerializer(serializers.ModelSerializer):
    food = FoodSerializer(source='food_id', read_only=True)

    class Meta:
        model = BuyurtmaItems
        fields = ['food', 'count', 'total_price']


class BuyurtmaSerializer(serializers.ModelSerializer):
    items = BuyurtmaItemInlineSerializer(many=True, write_only=True)
    items_detail = BuyurtmaItemReadSerializer(source='buyurtmaitems_set', many=True, read_only=True)
    promocode_id = serializers.PrimaryKeyRelatedField(
        queryset=Promocode.objects.all(),
        required=False,
        allow_null=True
    )

    class Meta:
        model = Buyurtma
        fields = [
            'id',
            'user_id',
            'manzil',
            'promocode_id',
            'items',
            'items_detail',  
            'total_price',
            'status',
            'promocode_applied',
            'created_at'
        ]
        read_only_fields = [
            'id',
            'user_id',
            'total_price',
            'status',
            'promocode_applied',
            'created_at'
        ]

    def create(self, validated_data):
        items_data = validated_data.pop('items')
        promocode = validated_data.pop('promocode_id', None)

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
