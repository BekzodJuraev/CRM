from django.db import models
from django.contrib.auth.models import User
from phonenumber_field.modelfields import PhoneNumberField


class Profile(models.Model):
    POSITION_CHOICES = [
        ("manager", "Менеджер"),
        ("admin", "Администратор"),
        ("supplier", "Снабженец"),
        ("chief", "Главный ЦЕХа"),
        ("installer", "Установщик"),
        ("technologist", "Технолог"),
        ("designer", "Дизайнер"),
    ]
    username = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    name = models.CharField(max_length=200, null=True, blank=True, default=None)
    lastname = models.CharField(max_length=200, null=True, blank=True, default=None)
    middle_name = models.CharField(max_length=200, null=True, blank=True, default=None)
    date_birth = models.DateField(null=True, blank=True, default=None)
    phone = PhoneNumberField()
    adress = models.CharField(max_length=200,blank=True)
    last_job=models.CharField(max_length=200,blank=True)
    work_exp=models.CharField(max_length=200,blank=True)
    position = models.CharField(max_length=20, choices=POSITION_CHOICES)
    hobby=models.CharField(max_length=60,blank=True)
    photo = models.ImageField(blank=True, upload_to='pictures/')
    approve=models.BooleanField(default=False)



class Stage(models.Model):
    name=models.CharField(max_length=30)

    def __str__(self):
        return self.name
class Orders(models.Model):
    client=models.CharField(max_length=250)
    adress=models.CharField(max_length=250)
    order_sum=models.IntegerField(default=0)
    order_predoplata=models.IntegerField(default=0)
    category=models.CharField(max_length=250)
    description=models.TextField()
    phone=models.CharField(max_length=50)
    social=models.CharField(max_length=60)
    stage=models.ForeignKey(Stage,on_delete=models.CASCADE, related_name='order')
    add_order=models.DateField()
    complete_order=models.DateField()



    def __str__(self):
        return self.client


class Consumables(models.Model):
    add=models.CharField(max_length=50)
    price=models.IntegerField()
    catigories=models.CharField(max_length=50)
    order = models.ForeignKey(Orders, on_delete=models.CASCADE, related_name='consumables')

    def __str__(self):
        return self.catigories


class Rezident(models.Model):
    company=models.CharField(max_length=60)
    photo = models.ImageField(blank=True, upload_to='pictures/')
    city=models.CharField(max_length=60)
    name=models.CharField(max_length=60)
    email=models.EmailField(blank=True)
    phone = PhoneNumberField()
    created_at = models.DateField(auto_now_add=True)

    def __str__(self):
        return self.company


class Finance(models.Model):
    name=models.CharField(max_length=60)
    sum=models.IntegerField(default=0)
    created_at=models.DateField(auto_now_add=True)

    def __str__(self):
        return self.name



class Debt(models.Model):
    order=models.ForeignKey(Orders,on_delete=models.CASCADE, related_name='debt')
    money_pay=models.DateField(blank=True,default=0)


    def __str__(self):
        return self.order.client




# class Warehouse(models.Model):
#     product=models.CharField(max_length=70)
#     quantity=models.IntegerField(default=0)
#     created_at=models.DateField(auto_now_add=True)
#     update_time=m