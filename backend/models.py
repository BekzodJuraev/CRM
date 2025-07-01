from django.db import models
from django.contrib.auth.models import User
from phonenumber_field.modelfields import PhoneNumberField


class Profile(models.Model):
    POSITION_CHOICES = [
        ("manager", "Менеджер"),
        ("admin", "Администратор"),
        ("accountant", "Бухгалтер"),
        ("supplier", "Снабженец"),
        ("chief", "Главный ЦЕХа"),
        ("chief_staff", "Сотрудник ЦЕХа"),
        ("delivery_cheif", "Главный доставщик"),
        ("delivery", "Доставщик"),
        ("installer_cheif", "Главный установщик"),
        ("installer", "Установщик"),
        ("technologist_cheif", "Главный Технолог"),
        ("technologist", "Технолог"),
        ("designer_cheif", "Главный дизайнер"),
        ("designer", "Дизайнер"),
        ("qa_cheif", "Главный сотрудник контроля качества"),
        ("qa_staff", "Сотрудник контроля качества"),
        ("sales_marketing", "Соц. маркетолог"),
        ("sales_call", "Сотрудник колл-центра"),

    ]
    username = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    name = models.CharField(max_length=200, null=True, blank=True, default=None)
    lastname = models.CharField(max_length=200, null=True, blank=True, default=None)
    middle_name = models.CharField(max_length=200, null=True, blank=True, default=None)
    date_birth = models.DateField(null=True, blank=True, default=None)
    phone = PhoneNumberField(blank=True)
    adress = models.CharField(max_length=200,blank=True)
    last_job=models.CharField(max_length=200,blank=True)
    work_exp=models.CharField(max_length=200,blank=True)
    position = models.CharField(max_length=20, choices=POSITION_CHOICES)
    hobby=models.CharField(max_length=60,blank=True)
    photo = models.ImageField(blank=True, upload_to='pictures/',null=True)
    approve=models.BooleanField(default=False)
    archive=models.BooleanField(default=True)



class Social_clients(models.Model):
    profile = models.ForeignKey(
        'Profile', on_delete=models.CASCADE, related_name='social_client', verbose_name="Профиль"
    )
    client_name=models.CharField(max_length=100)
    phone=PhoneNumberField(null=True, blank=True, default=None)
    comment=models.CharField(max_length=255,null=True, blank=True, default=None)
    order=models.OneToOneField("Orders", on_delete=models.CASCADE, related_name='marketing',null=True)


    def __str__(self):
        return self.profile.name

class Telegram_users(models.Model):
    phone = PhoneNumberField(blank=True)
    chat_id=models.IntegerField(default=0)


class Clients(models.Model):
    Social_CHOICES = [
        ("social", "Социальные сети"),
        ("cold_calls", "Холодные звонки"),
        ("word_of_mouth", "Сарафанное радио"),
    ]

    CLIENT_TYPE_CHOICES = [
        ('INDIVIDUAL', 'Физическое лицо'),
        ('LEGAL_ENTITY', 'Юридическое лицо'),
    ]

    social = models.CharField(max_length=20, choices=Social_CHOICES)



    client_type = models.CharField(
        max_length=20,
        choices=CLIENT_TYPE_CHOICES,
    )
    phone = PhoneNumberField()
    created_at = models.DateField(auto_now_add=True,null=True)

    #indivudal
    name = models.CharField(max_length=200, null=True, blank=True, default=None)
    lastname = models.CharField(max_length=200, null=True, blank=True, default=None)
    middle_name = models.CharField(max_length=200, null=True, blank=True, default=None)


    #legal
    adress = models.CharField(max_length=200, null=True, blank=True, default=None)
    company_name=models.CharField(max_length=200, null=True, blank=True, default=None)
    inn = models.CharField(max_length=12,null=True, blank=True, default=None)
    account=models.IntegerField(blank=True,null=True,default=None)
    mfo = models.IntegerField(blank=True, null=True, default=None)



    def __str__(self):
        return self.name or self.company_name


class Orders(models.Model):
    Stage_CHOICES = [
        ("marketing", "Соц. маркетинг"),
        ("call_center", "Колл-центр"),
        ("manager", "Менеджер"),
        ("design", "Проектирование"),
        ("technologist", "Технолог"),
        ("manager_2", "Менеджер_2"),
        ("accounting", "Бухгалтерия"),
        ("warehouse", "Склад"),

        ("manufacturing", "Производство"),
        ("assembly_stage", "Сборка"),
        ("accounting_2", "Бухгалтерия_2"),
        ("delivery", "Доставка"),
        ("installation", "Установка"),
        ("quality_control", "Контроль качества"),

        ("finished", "Завершён"),
        ("archive", "Архив"),
    ]
    Stage_pod_CHOICES = [
        ("rezka", "Резка"),
        ("svarka", "Сварка"),
        ("fill", "Покраска"),
        ("print", "Печать"),
    ]
    vstrecha_choice = [
        ("viezd", "Выезд"),
        ("priezd", "Приезд"),

    ]

    client=models.ForeignKey(Clients, on_delete=models.CASCADE, related_name='clients_order',null=True)
    order_name=models.CharField(max_length=100,null=True)
    vstrecha=models.CharField(max_length=20, choices=vstrecha_choice,null=True)
    order_sum=models.DecimalField(max_digits=10, decimal_places=2,default=0)
    order_predoplata=models.DecimalField(max_digits=10, decimal_places=2,default=0)
    description=models.TextField()
    description_design = models.TextField()
    check_design=models.BooleanField(default=False)
    catigories = models.CharField(max_length=50)
    razmer=models.CharField(max_length=50)

    latitude = models.FloatField(blank=True, null=True, default=0)
    longitude = models.FloatField(blank=True, null=True, default=0)
    tz=models.FileField(blank=True, upload_to='pictures/')
    design=models.FileField(blank=True, upload_to='pictures/')

    stage = models.CharField(max_length=20, choices=Stage_CHOICES,default='marketing')
    add_order=models.DateField(null=True)
    complete_order=models.DateField(null=True)
    rezka=models.BooleanField(default=False)
    svarka=models.BooleanField(default=False)
    fill=models.BooleanField(default=False)
    print=models.BooleanField(default=False)
    stage_pod=models.CharField(max_length=20, choices=Stage_pod_CHOICES,default="rezka")
    payment_data=models.DateField(null=True)
    complete_date=models.DateField(null=True)











class Delivery_Photo(models.Model):
    order = models.ForeignKey(Orders, on_delete=models.CASCADE, related_name='delivery_photo')
    photo=models.ImageField(blank=True, upload_to='delivery/')


class Compelete_Photo(models.Model):
    order = models.ForeignKey(Orders, on_delete=models.CASCADE, related_name='complete_photo')
    photo = models.ImageField(blank=True, upload_to='complete/')

class Consumables(models.Model):
    add=models.CharField(max_length=50)
    price=models.DecimalField(max_digits=10, decimal_places=2,default=0)
    catigories=models.CharField(max_length=50)
    order = models.ForeignKey(Orders, on_delete=models.CASCADE, related_name='consumables')
    quantity=models.IntegerField(default=1)





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
    sum=models.DecimalField(max_digits=10, decimal_places=2,default=0)
    created_at=models.DateField(auto_now_add=True)

    def __str__(self):
        return self.name



class Debt(models.Model):
    order=models.ForeignKey(Orders,on_delete=models.CASCADE, related_name='debt')
    money_pay=models.DateField(blank=True,default=0)


    def __str__(self):
        return self.order.client




class Warehouse(models.Model):
    product=models.CharField(max_length=70)
    quantity=models.IntegerField(default=0)
    created_at=models.DateField()
    category=models.CharField(max_length=70)
    city=models.CharField(max_length=70)
    deliver=models.CharField(max_length=70)




    def __str__(self):
        return self.product


class WarehouseLimit(models.Model):
    category = models.CharField(max_length=70)
    product = models.CharField(max_length=70)
    limit=models.IntegerField(default=0)

    def __str__(self):
        return self.product
