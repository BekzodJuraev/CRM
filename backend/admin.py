from django.contrib import admin
from .models import Profile,Orders,Rezident,Finance,Consumables,Debt,Warehouse,WarehouseLimit,Delivery_Photo,Compelete_Photo,Telegram_users,Clients,Social_clients,OrderStaff,Notification,Manager_Photo,Payments


@admin.register(Payments)
class Payments(admin.ModelAdmin):
    pass
# Register your models here.
@admin.register(Manager_Photo)
class Manager_Photo(admin.ModelAdmin):
    pass
@admin.register(Notification)
class Notification(admin.ModelAdmin):
    pass
@admin.register(OrderStaff)
class OrderStaff(admin.ModelAdmin):
    pass

@admin.register(Social_clients)
class Social_clients(admin.ModelAdmin):
    pass
@admin.register(Clients)
class ClientsAdmin(admin.ModelAdmin):
    pass
@admin.register(Telegram_users)
class Telegram(admin.ModelAdmin):
    pass
@admin.register(Delivery_Photo)
class Delivery_Photo(admin.ModelAdmin):
    pass
@admin.register(Compelete_Photo)
class Compelete_Photo(admin.ModelAdmin):
    pass
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
    list_display = ['add','warehouse']

