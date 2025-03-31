from django.contrib import admin
from .models import Profile,Orders,Rezident,Finance,Consumables
# Register your models here.
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

