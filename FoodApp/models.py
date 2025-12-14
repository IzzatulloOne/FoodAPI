from django.db import models
from django.contrib.auth.models import AbstractUser


class CustomUser(AbstractUser):
    phone = models.CharField(max_length=13, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    role = models.BooleanField(default=False)

    def __str__(self):
        return self.username


class Food(models.Model):
    nomi = models.CharField(max_length=100)
    description = models.TextField()
    narxi = models.DecimalField(max_digits=6, decimal_places=2)
    image = models.ImageField(upload_to='food_images/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    chegirma_id = models.IntegerField(blank=True, null=True)

    def __str__(self):
        return self.nomi
    

class Promocode(models.Model):
    nomi = models.CharField(max_length=50)
    discount_amount = models.DecimalField(max_digits=8, decimal_places=2)
    max_discount = models.DecimalField(max_digits=8, decimal_places=2)
    usage_limit = models.IntegerField()
    used_count = models.IntegerField(default=0)
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()

    def is_active(self):
        from django.utils.timezone import now
        return (
            self.start_date <= now() <= self.end_date
            and self.used_count < self.usage_limit
        )
    
    def __str__(self):
        return self.nomi
    

class Buyurtma(models.Model):
    STATUS_CHOICES = [
        ('yangi', 'Yangi'),
        ('tayyorlanmoqda', 'Tayyorlanmoqda'),
        ('yolda', 'Yolda'),
        ('yetkazildi', 'Yetkazildi'),
        ('bekor_qilindi', 'Bekor qilindi'),
    ]

    user_id = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    manzil = models.CharField(max_length=255)
    total_price = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    promocode_id = models.ForeignKey(Promocode, on_delete=models.SET_NULL, blank=True, null=True)
    promocode_applied = models.BooleanField(default=False)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='yangi')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Buyurtma {self.id} - {self.user_id.username}"



class BuyurtmaItems(models.Model):
    food_id = models.ForeignKey(Food, on_delete=models.CASCADE)
    count = models.IntegerField()
    total_price = models.DecimalField(max_digits=8, decimal_places=2)
    buyurtma_id = models.ForeignKey(Buyurtma, on_delete=models.CASCADE)