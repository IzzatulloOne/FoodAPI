from rest_framework.serializers import ModelSerializer
from rest_framework import serializers
from .models import Food, Promocode, Buyurtma, BuyurtmaItems, CustomUser


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
    food = serializers.PrimaryKeyRelatedField(source='food_id', queryset=Food.objects.all())

    class Meta:
        model = BuyurtmaItems
        fields = ['id', 'food', 'count', 'total_price', 'buyurtma_id']
        read_only_fields = ['id', 'total_price']

    def create(self, validated_data):
        buyurtma = validated_data['buyurtma_id']

        if buyurtma.status != 'yangi':
            raise serializers.ValidationError("Buyurtma holati o'zgargan, mahsulot qo'shib bo'lmaydi")

        food = validated_data.pop('food_id')
        count = validated_data['count']

        validated_data['total_price'] = max(food.narxi * count, 0)
        validated_data['food_id'] = food

        item = super().create(validated_data)

        buyurtma.total_price = sum(i.total_price for i in buyurtma.buyurtmaitems_set.all())
        buyurtma.save()

        return item


class BuyurtmaSerializer(serializers.ModelSerializer):
    promocode = serializers.PrimaryKeyRelatedField(
        source='promocode_id',
        queryset=Promocode.objects.all(),
        required=False,
        allow_null=True
    )

    class Meta:
        model = Buyurtma
        fields = ['id', 'user_id', 'manzil', 'total_price', 'promocode', 'promocode_applied', 'status', 'created_at']
        read_only_fields = ['id', 'created_at', 'total_price']

    def update(self, instance, validated_data):
        instance = super().update(instance, validated_data)

        items_total = sum(item.food_id.narxi * item.count for item in instance.buyurtmaitems_set.all())
        discount = 0
        promocode = validated_data.get('promocode_id') or instance.promocode_id

        if promocode and not instance.promocode_applied and instance.status == 'yangi':
            if promocode.is_active():
                discount = min(promocode.discount_amount, promocode.max_discount)
                promocode.used_count += 1
                promocode.save()
                instance.promocode_applied = True

        instance.total_price = max(items_total - discount, 0)
        instance.save()

        return instance
