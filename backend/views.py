from django.shortcuts import render
from django.http import HttpResponse
from django.views.generic import View,TemplateView
from django.urls import reverse_lazy
class Main(TemplateView):
   template_name = 'main.html'

class Login(TemplateView):
   template_name = 'login.html'

class Register(TemplateView):
   template_name = 'register.html'



