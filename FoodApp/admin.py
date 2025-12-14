from django.contrib import admin
from . import models


admin.site.register(models.CustomUser)
admin.site.register(models.Food)
admin.site.register(models.Promocode)
admin.site.register(models.Buyurtma)
admin.site.register(models.BuyurtmaItems)