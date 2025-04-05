from django.urls import path,include
from . import views


urlpatterns=[
    path('',views.Main.as_view(),name='main'),
    path('login/',views.Login.as_view(),name='login'),
    path('register/',views.Register.as_view(),name='register')
]