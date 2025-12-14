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


class BuyurtmaSerializer(ModelSerializer):
    class Meta:
        model = Buyurtma
        fields = '__all__'
        read_only_fields = ['id', 'created_at', 'total_price']

    def update(self, instance, validated_data):
        instance = super().update(instance, validated_data)

        items_total = sum(
            item.food_id.narxi * item.count
            for item in instance.buyurtmaitems_set.all()
        )

        discount = 0
        promocode = instance.promocode_id

        if promocode and not instance.promocode_applied:
            if instance.status != 'yangi':
                raise serializers.ValidationError(
                    "Promokod faqat yangi buyurtmaga qo'llanadi"
                )

            if promocode.is_active():
                discount = min(promocode.discount_amount, promocode.max_discount)
                promocode.used_count += 1
                promocode.save()
                instance.promocode_applied = True

        instance.total_price = max(items_total - discount, 0)
        instance.save()

        return instance




class BuyurtmaItemsSerializer(ModelSerializer):
    class Meta:
        model = BuyurtmaItems
        fields = '__all__'
        read_only_fields = ['id', 'total_price']

    def create(self, validated_data):
        buyurtma = validated_data['buyurtma_id']

        if buyurtma.status != 'yangi':
            raise serializers.ValidationError(
                "Buyurtma holati o'zgargan, mahsulot qo'shib bo'lmaydi"
            )

        food = validated_data['food_id']
        count = validated_data['count']
        buyurtma = validated_data['buyurtma_id']

        item_price = food.narxi * count
        if item_price < 0:
            item_price = 0

        validated_data['total_price'] = item_price

        item = super().create(validated_data)

        items = buyurtma.buyurtmaitems_set.all()
        new_total = sum(i.total_price for i in items)
        buyurtma.total_price = new_total
        buyurtma.save()

        return item