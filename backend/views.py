from django.shortcuts import render,redirect
from django.http import HttpResponse
from django.views.generic import View,TemplateView
from .models import Profile
from django.contrib.auth.models import User
from django.urls import reverse_lazy
from django.contrib.auth import authenticate,login,logout


class Dashboard(TemplateView):
   template_name = 'dashboard.html'

class Main(TemplateView):
   template_name = 'main.html'


class Login(TemplateView):
   template_name = 'login.html'

   def post(self, request, *args, **kwargs):
      username = request.POST.get('username')
      password = request.POST.get('password')
      next_url = request.GET.get('next')

      # Error handling
      errors = {}



      if not errors:
         user = authenticate(username=username, password=password)
         if user:
            login(request, user)
            return redirect(next_url if next_url else 'dashboard')
         else:
            errors['invalid'] = 'Неверное имя пользователя или пароль'


      return render(request, self.template_name, {'errors': errors})


class Register(TemplateView):
   template_name = 'register.html'

   def  post(self, request, *args, **kwargs):
      name = request.POST.get('name')
      lastname = request.POST.get('lastname')
      middle_name = request.POST.get('middle_name')
      date_birth = request.POST.get('date_birth')
      phone = request.POST.get('phone')
      adress = request.POST.get('adress')
      last_job = request.POST.get('last_job')
      work_exp = request.POST.get('work_exp')
      position = request.POST.get('position')
      hobby = request.POST.get('hobby')
      photo = request.FILES.get('photo')
      password=request.POST.get('password')
      errors={}
      if User.objects.filter(username=name).exists():
         errors['username'] = "Пользователь с таким именем уже существует"

      if not password or len(password) < 6:
         errors['password'] = "Пароль должен содержать не менее 6 символов"

      if not photo:
         errors['photo'] = "Пожалуйста, загрузите фото"

      if errors:
         return render(request, self.template_name, {'errors': errors, 'data': request.POST})
      user=User.objects.create_user(username=name,password=password)
      Profile.objects.create(
         username=user,
         name=name,
         lastname=lastname,
         middle_name=middle_name,
         date_birth=date_birth,
         phone=phone,
         adress=adress,
         last_job=last_job,
         work_exp=work_exp,
         position=position,
         hobby=hobby,
         photo=photo
      )

      return redirect('login')










