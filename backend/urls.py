from django.urls import path,include
from . import views


urlpatterns=[
    path('',views.Main.as_view(),name='main'),
    path('login/',views.Login.as_view(),name='login'),
    path('register/',views.Register.as_view(),name='register'),
    path('dashboard/',views.Dashboard.as_view(),name='dashboard'),
    path('order/',views.Order.as_view(),name='order'),
    path('applications/',views.Applications.as_view(),name='apply'),
    path('staff/',views.Staff.as_view(),name='staff')
]