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
    class Meta:
        model = BuyurtmaItems
        fields = ['food', 'count']

class BuyurtmaSerializer(serializers.ModelSerializer):
    items = BuyurtmaItemsSerializer(many=True, write_only=True)

    class Meta:
        model = Buyurtma
        fields = ['id', 'manzil', 'promocode', 'items', 'total_price']
        read_only_fields = ['id', 'total_price']

    def create(self, validated_data):
        items_data = validated_data.pop('items')
        buyurtma = Buyurtma.objects.create(**validated_data)

        total_price = 0
        for item_data in items_data:
            food = item_data['food']
            count = item_data['count']
            price = food.narxi * count
            BuyurtmaItems.objects.create(buyurtma=buyurtma, food=food, count=count, total_price=price)
            total_price += price

        buyurtma.total_price = total_price
        buyurtma.save()
        return buyurtma
