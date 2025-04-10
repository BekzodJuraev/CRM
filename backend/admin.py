from django.contrib import admin
from .models import Profile,Orders,Rezident,Finance,Consumables,Debt,Warehouse,WarehouseLimit
# Register your models here.

@admin.register(WarehouseLimit)
class WarehouseLimit(admin.ModelAdmin):
    list_display = ['product']
@admin.register(Warehouse)
class Warehouse(admin.ModelAdmin):
    list_display = ['product']
@admin.register(Debt)
class Debt(admin.ModelAdmin):
    list_display = ['order']
@admin.register(Profile)
class Profile(admin.ModelAdmin):
    list_display = ['name']

@admin.register(Orders)
class Orders(admin.ModelAdmin):
    pass


@admin.register(Rezident)
class Rezident(admin.ModelAdmin):
    pass


@admin.register(Finance)
class Finance(admin.ModelAdmin):
    pass


@admin.register(Consumables)
class Consumables(admin.ModelAdmin):
    pass

