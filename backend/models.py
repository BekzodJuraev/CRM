from django.db import models
from django.contrib.auth.models import User
from phonenumber_field.modelfields import PhoneNumberField


class Profile(models.Model):
    username = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    name = models.CharField(max_length=200, null=True, blank=True, default=None)
    lastname = models.CharField(max_length=200, null=True, blank=True, default=None)
    middle_name = models.CharField(max_length=200, null=True, blank=True, default=None)
    date_birth = models.DateField(null=True, blank=True, default=None)
    phone = PhoneNumberField()
    adress = models.CharField(max_length=200,blank=True)
    last_job=models.CharField(max_length=200,blank=True)
    work_exp=models.CharField(max_length=200,blank=True)
    postion=models.CharField(max_length=200)
    photo = models.ImageField(blank=True, upload_to='pictures/')



