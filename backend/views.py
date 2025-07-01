import time
from django.db import connection, reset_queries
from django.http import JsonResponse

from django.shortcuts import render,redirect
from django.http import HttpResponse
from django.views.generic import View,TemplateView,DetailView,UpdateView
from .models import Profile,Rezident,Finance,Warehouse,WarehouseLimit,Consumables,Orders,Delivery_Photo,Compelete_Photo,Telegram_users,Clients,Social_clients
from django.contrib.auth.models import User
from django.urls import reverse_lazy
from django.contrib.auth import authenticate,login,logout
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Sum,Q,Count,F,Max,Prefetch,OuterRef, Subquery,Value
from django.utils.timezone import now
from django.http import JsonResponse
from django.contrib.auth.views import LogoutView
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
import telegram
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton,WebAppInfo
import json


bot = telegram.Bot("8184436447:AAF3WD9vRZO5C3IiY3WBgZ9I2Oht45ZCt3c")


def search_client(request):
   query = request.GET.get('q')
   client_id = request.GET.get('id')
   client_type = request.GET.get('type')
   if client_type == 'legal':


      if client_id:

         try:
            c = Clients.objects.get(id=client_id)

            return JsonResponse({
               'id': c.id,
               'company_name': c.company_name,
               'inn': c.inn,
               'account':c.account,
               'mfo': c.mfo,
               'adress':c.adress,
               'phone': str(c.phone),
               'source': c.get_social_display(),
               'registered_at': c.created_at.strftime('%d.%m.%Y') if c.created_at else ''
            })
         except Clients.DoesNotExist:
            return JsonResponse({'error': 'Клиент не найден'}, status=404)

      if query:
         clients = Clients.objects.filter(company_name__icontains=query)[:10]

         results = [
            {
               'id': c.id,
               'name': c.company_name
            }
            for c in clients
         ]
         return JsonResponse(results, safe=False)

      return JsonResponse([], safe=False)

   else:
      if client_id:
         try:
            c = Clients.objects.get(id=client_id)
            return JsonResponse({
               'id': c.id,
               'name': c.name,
               'lastname': c.lastname,
               'middle_name': c.middle_name,
               'phone': str(c.phone),
               'source': c.get_social_display(),
               'registered_at': c.created_at.strftime('%d.%m.%Y') if c.created_at else ''
            })
         except Clients.DoesNotExist:
            return JsonResponse({'error': 'Клиент не найден'}, status=404)

      if query:
         clients = Clients.objects.filter(
            Q(name__icontains=query) |
            Q(lastname__icontains=query) |
            Q(middle_name__icontains=query)
         )[:10]

         results = [
            {
               'id': c.id,
               'name': f"{c.lastname or ''} {c.name or ''} {c.middle_name or ''}".strip()
            }
            for c in clients
         ]
         return JsonResponse(results, safe=False)

      return JsonResponse([], safe=False)



@csrf_exempt
@require_POST
def telegram_webhook(request):
    if request.method == 'POST':
        try:
            json_data = json.loads(request.body.decode('utf-8'))
            if 'message' in json_data:
                process_message(json_data)
            elif 'callback_query' in json_data:
                process_callback_query(json_data)
        except:
            pass

        return HttpResponse(status=200)
    else:
        return HttpResponse(status=405)

reply_keyboard = [
    [KeyboardButton("📞Отправить номер телефона",request_contact=True)],
]
markup_reply = ReplyKeyboardMarkup(reply_keyboard, resize_keyboard=True)
def process_message(json_data):
   chat_id = json_data['message']['chat']['id']
   message_text = json_data['message'].get('text', "")


   if message_text == "/start":
      bot.send_message(chat_id,text="👋 Здравствуйте! Это бот для отслеживания статуса вашего заказа.📱 Пожалуйста, отправьте свой номер телефона, чтобы мы могли проверить ваш заказ в системе.",reply_markup=markup_reply)

   elif 'contact' in json_data['message']:
      phone_number = json_data['message']['contact']['phone_number']
      order=Orders.objects.filter(phone=phone_number)
      profile=Profile.objects.filter(phone=phone_number)
      if order:
         Telegram_users.objects.get_or_create(phone=phone_number,chat_id=chat_id)
      elif profile:
         Telegram_users.objects.get_or_create(phone=phone_number,chat_id=chat_id)
      else:
         bot.send_message(chat_id,text="❌ Ваш номер не зарегистрирован в системе.")



def process_callback_query(json_data):
   pass




def logout_view(request):
   logout(request)
   return redirect('main')

def admin_tech(pk):
   postion=['manager','admin','chief']
   profile = Profile.objects.filter(position__in=postion).values_list('phone', flat=True)
   zakaz = Orders.objects.filter(pk=pk).first()
   telegram_users = Telegram_users.objects.filter(phone__in=profile)
   text = (f"🚚 Заказ готов к доставке!"
           f"\n📌 Клиент {zakaz.client}"
           f"\n📞 Контакт заказчика: {zakaz.phone}"
           f"\n📍 Адрес:: {zakaz.adress}"
           f"\n💵 Общая сумма заказа: {zakaz.order_sum}"
           f"\n💰 Остаток к оплате: {zakaz.order_sum - zakaz.order_predoplata} сум📍 "
           f"\n📅 Срок выполнения: {zakaz.complete_order}")

   for item in telegram_users:
      try:
         bot.send_message(item.chat_id, text=text)
      except:
         pass





def mess(pk):
   zakaz = Orders.objects.filter(pk=pk).first()
   telegram_user = Telegram_users.objects.filter(phone=zakaz.phone).first()
   categories = ', '.join(str(consumable) for consumable in zakaz.consumables.all())

   text = (f"🔔 Обновление статуса заказа!"
           f"\n🏷️ {zakaz.client}"
           f"\nСрок выполнения: {zakaz.complete_order}"
           f"\n📂 Категория: {categories}"
           f"\n📝 Описание / ТЗ: {zakaz.description}"
           f"\nСумма заказа: {zakaz.order_sum} сум📍 "
           f"\n📍Ваш заказ перенесён на этап \"{zakaz.get_stage_display()}\".")

   try:
      bot.send_message(chat_id=telegram_user.chat_id, text=text)
   except:

      pass


class Dashboard(LoginRequiredMixin,TemplateView):
   login_url = reverse_lazy('login')
   template_name = 'dashboard.html'




   def post(self,request):
      action=request.POST.get('action')
      pk = request.POST.get('pk')
      stage=request.POST.get('stage')



      if action == "designer":
         Orders.objects.filter(pk=pk).update(stage="technologist")
         mess(pk)

         return redirect(request.path)
      elif action == "technologist":
         add = request.POST.getlist('add')
         price = request.POST.getlist('price')
         catigories = request.POST.getlist('catigories')
         quantity=request.POST.getlist('quantity')
         quantity=request.POST.getlist('quantity')
         rezka = request.POST.get('rezka') == 'on'
         svarka = request.POST.get('svarka') == 'on'
         fill = request.POST.get('fill') == 'on'
         pechat = request.POST.get('print') == 'on'

         if rezka:
            pod_stage="rezka"
         elif svarka:
            pod_stage="svarka"
         elif fill:
            pod_stage="fill"
         elif pechat:
            pod_stage="print"


         Orders.objects.filter(pk=pk).update(stage="manufacturing",stage_pod=pod_stage,rezka=rezka,svarka=svarka,fill=fill,print=pechat)
         consumables = [
            Consumables(order_id=pk, add=a, price=p, catigories=c, quantity=d)
            for a, p, c, d in zip(add, price, catigories, quantity)
         ]
         Consumables.objects.bulk_create(consumables)

         mess(pk)

         return redirect(request.path)
      elif action == "delivery":
         photo = request.FILES.getlist('photo')

         order=Orders.objects.filter(pk=pk).update(stage='order_ready')
         delivery = [
            Delivery_Photo(order_id=pk, photo=p)
            for p in photo
         ]
         Delivery_Photo.objects.bulk_create(delivery)


         mess(pk)

         return redirect(request.path)

      elif action == 'chief':
         stage_pod=request.POST.get('pod_stage')
         order=Orders.objects.filter(pk=pk).first()
         check=getattr(order,stage_pod,None)


         if check is False:
            services = []
            if order.rezka:
               services.append("Резка")
            if order.svarka:
               services.append("Сварка")
            if order.fill:
               services.append("Покраска")
            if order.print:
               services.append("Печать")

            x = ", ".join(services)
            return JsonResponse({'message': f'Для данного проекта технолог выбрал только этапы: {x}'}, status=401)



         if stage_pod:
            Orders.objects.filter(pk=pk).update(stage=stage,stage_pod=stage_pod)
         else:
            Orders.objects.filter(pk=pk).update(stage=stage)
            mess(pk)
         if stage == "delivery":
            admin_tech(pk)



         return JsonResponse({'status': 'success'})



      elif action == "admin":
         if stage == "finished":
            Orders.objects.filter(pk=pk).update(stage=stage, complete_date=now().date())

         elif stage == 'delivery':
            Orders.objects.filter(pk=pk).update(stage=stage)
            admin_tech(pk)
         else:
            Orders.objects.filter(pk=pk).update(stage=stage)


         mess(pk)





         return JsonResponse({'status': 'success'})
      return JsonResponse({'status': 'error', 'message': 'Invalid action'}, status=400)





   def get_context_data(self, *, object_list=None, **kwargs):
      context = super().get_context_data(**kwargs)
      search = self.request.GET.get('search')

      stages = [
         "marketing",
         "call_center",
         "manager",
         "design",
         "technologist",
         "manager_2",
         "accounting",
         "warehouse",
         "manufacturing",
         "assembly_stage",
         "accounting_2",
         "delivery",
         "installation",
         "quality_control",
         "finished",
      ]


      for stage in stages:
         queryset = Orders.objects.filter(stage=stage).prefetch_related('consumables').annotate(today=Value(now().date()))



         if search:
            queryset = queryset.filter(client__icontains=search)



         context[stage] = queryset



      context['rezka'] = [o for o in context['manufacturing'] if o.stage_pod == 'rezka']
      context['svarka'] = [o for o in context['manufacturing'] if o.stage_pod == 'svarka']
      context['fill'] = [o for o in context['manufacturing'] if o.stage_pod == 'fill']
      context['print'] = [o for o in context['manufacturing'] if o.stage_pod == 'print']


      return context









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
      login=request.POST.get('login')
      phone = request.POST.get('phone')
      adress = request.POST.get('adress')
      last_job = request.POST.get('last_job')
      work_exp = request.POST.get('work_exp')
      position = request.POST.get('position')
      hobby = request.POST.get('hobby')
      photo = request.FILES.get('photo')
      password=request.POST.get('password')
      errors={}
      if User.objects.filter(username=login).exists():
         errors['username'] = "Пользователь с таким логином уже существует"

      if not password or len(password) < 6:
         errors['password'] = "Пароль должен содержать не менее 6 символов"

      if not photo:
         errors['photo'] = "Пожалуйста, загрузите фото"

      if errors:
         return render(request, self.template_name, {'errors': errors, 'data': request.POST})
      user=User.objects.create_user(username=login,password=password)
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

class Staff_more(LoginRequiredMixin,TemplateView):
   login_url = reverse_lazy('login')
   template_name = 'staff_more.html'
class OrderDetail(LoginRequiredMixin,DetailView):
   model = Orders
   login_url = reverse_lazy('login')
   template_name = 'order_detail.html'
   context_object_name = 'item'

   def post(self, request, *args, **kwargs):
      self.object = self.get_object()

      # Update fields from form data
      self.object.client = request.POST.get('client')
      self.object.adress = request.POST.get('adress')
      self.object.order_sum = request.POST.get('order_sum')
      self.object.order_predoplata = request.POST.get('order_predoplata')
      self.object.description = request.POST.get('description')
      self.object.phone = request.POST.get('phone')
      self.object.social = request.POST.get('social')
      self.object.stage = request.POST.get('stage')
      self.object.add_order = request.POST.get('add_order')
      self.object.complete_order = request.POST.get('complete_order')

      # Handle uploaded file (delivery photo)


      # Save the updated order
      self.object.save()

      photo=request.FILES.getlist('delivery_photo')
      delivery = [
         Compelete_Photo(order=self.object, photo=p)
         for p in photo
      ]
      Compelete_Photo.objects.bulk_create(delivery)

      # Handle Consumables data
      add = request.POST.getlist('add')
      price = request.POST.getlist('price')
      catigories = request.POST.getlist('catigories')
      quantity = request.POST.getlist('quantity')

      # Delete old consumables for this order to avoid duplication
      Consumables.objects.filter(order=self.object).delete()

      # Create new consumables
      consumables = [
         Consumables(order=self.object, add=a, price=p, catigories=c, quantity=d)
         for a, p, c, d in zip(add, price, catigories, quantity)
      ]
      Consumables.objects.bulk_create(consumables)
      mess(self.object.pk)

      # Redirect after successful update
      return redirect('dashboard')



class Order(LoginRequiredMixin,TemplateView):
   template_name = 'order.html'
   login_url = reverse_lazy('login')


   def post(self,request):
      # add=request.POST.getlist('add')
      # price=request.POST.getlist('price')
      # catigories = request.POST.getlist('catigories')
      # quantity=request.POST.getlist('quantity')



      client = request.POST.get('client_id')
      vstrecha=request.POST.get('vstrecha')
      order_name=request.POST.get('order_name')
      order_sum = request.POST.get('order_sum')
      catigories=request.POST.get('catigories')
      order_predoplata = request.POST.get('order_predoplata')
      tz=request.FILES.get('tz')
      check_design=request.POST.get('check_design') == 'on'
      design = request.FILES.get('design')
      latitude=request.POST.get('latitude')
      longitude=request.POST.get('longitude')
      razmer=request.POST.get('razmer')
      description = request.POST.get('description')
      description_design=request.POST.get('description_design')


      stage = request.POST.get('stage')
      add_order = request.POST.get('add_order')
      complete_order = request.POST.get('complete_order')



      order=Orders.objects.create\
         (client_id=client,
          order_name=order_name,
          vstrecha=vstrecha,
          order_sum=order_sum,
          order_predoplata=order_predoplata,
          description=description,
          catigories=catigories,
          tz=tz,
          check_design=check_design,
          design=design,
          latitude=latitude,
          longitude=longitude,
          razmer=razmer,
          description_design=description_design,
          stage=stage,
          add_order=add_order,
          complete_order=complete_order

          )


     # mess(order.pk)

      return redirect('dashboard')


class ProfileView(LoginRequiredMixin,TemplateView):
   template_name = 'profile.html'
   login_url = reverse_lazy('login')
   def post(self, request, *args, **kwargs):
      profile = request.user.profile
      action=request.POST.get('action')
      photo = request.FILES.get('photo')
      if action == "delete":
         profile.photo=None
         profile.save(update_fields=['photo'])
      else:
         profile.photo=photo
         profile.save(update_fields=['photo'])


      return redirect(request.path)

class Applications(LoginRequiredMixin,TemplateView):
   template_name = 'applications.html'
   login_url = reverse_lazy('login')

   def post(self, request, *args, **kwargs):
      action=request.POST.get('action')
      pk = request.POST.get('pk')

      if action == "approve":
         Profile.objects.filter(id=pk).update(approve=True)
      else:
         User.objects.filter(profile__id=pk).delete()
         #Profile.objects.filter(id=pk).delete()


      return redirect(request.path)







   def get_context_data(self, *, object_list=None, **kwargs):
      context = super().get_context_data(**kwargs)

      context['profile']=Profile.objects.filter(approve=False).order_by('-id')

      return context


class Staff(LoginRequiredMixin,TemplateView):
   template_name = 'staff.html'
   login_url = reverse_lazy('login')

   def post(self,request):
      pk=self.request.POST.get('pk')
      profile = Profile.objects.select_related('username').get(pk=pk)
      profile.archive = False
      profile.username.is_active = False
      profile.username.save(update_fields=['is_active'])
      profile.save(update_fields=['archive'])

      return redirect(request.path)





   def get_context_data(self, *, object_list=None, **kwargs):
      context = super().get_context_data(**kwargs)
      search=self.request.GET.get('search')

      if search:
         # Apply a case-insensitive search across multiple fields
         context['profile'] = Profile.objects.filter(
            approve=True,
            archive=True
         ).filter(
            Q(name__icontains=search) |
            Q(lastname__icontains=search) |
            Q(middle_name__icontains=search)  # Add more fields as necessary
         ).order_by('-id')
      else:
         # Return all profiles if no search term is provided
         context['profile'] = Profile.objects.filter(approve=True,archive=True).order_by('-id')



      return context

class StaffArchive(LoginRequiredMixin,TemplateView):
   template_name = 'staff_archive.html'
   login_url = reverse_lazy('login')

   def post(self,request):
      pk=self.request.POST.get('pk')
      profile = Profile.objects.select_related('username').get(pk=pk)
      profile.archive = True
      profile.username.is_active = True
      profile.username.save(update_fields=['is_active'])
      profile.save(update_fields=['archive'])

      return redirect(request.path)





   def get_context_data(self, *, object_list=None, **kwargs):
      context = super().get_context_data(**kwargs)
      search=self.request.GET.get('search')

      if search:
         # Apply a case-insensitive search across multiple fields
         context['profile'] = Profile.objects.filter(
            approve=True,
            archive=False
         ).filter(
            Q(name__icontains=search) |
            Q(lastname__icontains=search) |
            Q(middle_name__icontains=search)  # Add more fields as necessary
         ).order_by('-id')
      else:
         # Return all profiles if no search term is provided
         context['profile'] = Profile.objects.filter(approve=True,archive=False).order_by('-id')



      return context

class RezidentView(LoginRequiredMixin,TemplateView):
   template_name = 'rezedent.html'
   login_url = reverse_lazy('login')

   def get_context_data(self, *, object_list=None, **kwargs):
      context = super().get_context_data(**kwargs)
      search=self.request.GET.get('search')

      if search:
         context['rezident'] = Rezident.objects.filter(
            Q(company__icontains=search) |
            Q(name__icontains=search) |
            Q(email__icontains=search)
         )
      else:
         context['rezident'] = Rezident.objects.all()




      return context



class Rezident_Create(LoginRequiredMixin,TemplateView):
   template_name = 'rezident_add.html'
   login_url = reverse_lazy('login')

   def post(self, request, *args, **kwargs):
      photo = request.FILES.get('photo')
      company=request.POST.get('company')
      city = request.POST.get('city')
      name = request.POST.get('name')
      phone = request.POST.get('phone')
      email= request.POST.get('email')


      Rezident.objects.create(
         photo=photo,
         company=company,
         city=city,
         name=name,
         phone=phone,
         email=email
      )



      return redirect('rezident')



class ClietView(LoginRequiredMixin,TemplateView):
   template_name = 'client_list.html'
   login_url = reverse_lazy('login')

   def get_context_data(self, *, object_list=None, **kwargs):
      context = super().get_context_data(**kwargs)
      context['client_fiz']=Clients.objects.filter(client_type='INDIVIDUAL')
      context['client_leg'] = Clients.objects.filter(client_type='LEGAL_ENTITY')

      return context


class ClientCreateView(LoginRequiredMixin,TemplateView):
   template_name = 'client_add.html'
   login_url = reverse_lazy('login')


   def post(self, request, *args, **kwargs):
      action=request.POST.get('action')
      phone=request.POST.get('phone')
      social=request.POST.get('social')
      if action == 'INDIVIDUAL':
         name=request.POST.get('name')
         lastname = request.POST.get('lastname')
         middle_name = request.POST.get('middle_name')
         Clients.objects.create(name=name,lastname=lastname,middle_name=middle_name,social=social,phone=phone,client_type=action)
      else:
         adress = request.POST.get('adress')
         company_name = request.POST.get('company_name')
         inn = request.POST.get('inn')
         account = request.POST.get('account')
         mfo = request.POST.get('mfo')
         Clients.objects.create(adress=adress, company_name=company_name, inn=inn, social=social, phone=phone,
                                client_type='LEGAL_ENTITY',account=account,mfo=mfo)

      return redirect('clients')

class MarketingClietView(LoginRequiredMixin,TemplateView):
   template_name = 'marketing.html'
   login_url = reverse_lazy('login')


   def post(self, request, *args, **kwargs):
      pk = request.POST.get('pk')
      Orders.objects.filter(marketing__id=pk).update(stage='call_center')
      return redirect(request.path)



class ArchiveOrder(LoginRequiredMixin,TemplateView):
   template_name = 'archive.html'
   login_url = reverse_lazy('login')
   def get_context_data(self, *, object_list=None, **kwargs):
      context = super().get_context_data(**kwargs)
      search = self.request.GET.get('search')
      profile=self.request.user.profile

      if search:
         context['profile'] = Social_clients.objects.filter(profile=profile,client_name__icontains=search).select_related('order')
      else:
         context['profile'] = Social_clients.objects.filter(profile=profile).select_related('order')

      return context

class DetailMarketing(LoginRequiredMixin,DetailView):
   model = Social_clients
   login_url = reverse_lazy('login')
   template_name = 'marketing_detail.html'
   context_object_name = 'item'

   def post(self, request, *args, **kwargs):
      phone = request.POST.get('phone')
      client_name = request.POST.get('client')
      comment = request.POST.get('comment')
      self.object = self.get_object()
      self.object.phone=phone
      self.object.client_name=client_name
      self.object.comment=comment
      self.object.save()

      return redirect('marketing')

class MarketingClientCreateView(LoginRequiredMixin,TemplateView):
   template_name = 'marketing_add.html'
   login_url = reverse_lazy('login')


   def post(self, request, *args, **kwargs):

      phone=request.POST.get('phone')
      client_name = request.POST.get('client')
      comment = request.POST.get('comment')
      profile=request.user.profile
      order=Orders.objects.create()
      Social_clients.objects.create(profile=profile,client_name=client_name,phone=phone,comment=comment,order=order)




      return redirect('marketing')
class Money(LoginRequiredMixin,TemplateView):
   template_name = 'money.html'
   login_url = reverse_lazy('login')

   def get_context_data(self, *, object_list=None, **kwargs):
      context = super().get_context_data(**kwargs)
      first = self.request.GET.get('first')
      second=self.request.GET.get('second')
      rasxod=self.request.GET.get('rasxod')

      today = now()
      query=Finance.objects.filter(
          created_at__year=today.year,
          created_at__month=today.month
      ).order_by('-id')

      order = Orders.objects.filter(stage="finished", complete_date__year=today.year,
                                    complete_date__month=today.month)
      order1 = Orders.objects.filter(complete_date__year=today.year,
                                    complete_date__month=today.month)


      if first and second:
         if rasxod:
            query = query.filter(created_at__range=(first, second), name=rasxod)
         else:
            query = query.filter(created_at__range=(first, second))


         order=order.filter(complete_date__range=(first,second))
         order1=order1.filter(complete_date__range=(first,second))

      marja=Consumables.objects.filter(order__in=order).aggregate(total_sum=Sum(F('price')*F('quantity')))['total_sum'] or 0
      marja1 = Consumables.objects.filter(order__in=order1).aggregate(total_sum=Sum(F('price') * F('quantity')))[
                 'total_sum'] or 0

      total_sum=order.aggregate(total_sum=Sum('order_sum'))['total_sum'] or 0
      cost=query.aggregate(total_sum=Sum('sum'))['total_sum'] or 0
      context['today_day']=today
      context['first_day']=today.replace(day=1)


      context['marja']=total_sum - marja
      context['money'] = query
      context['count']=order.count()
      context['total_sum']=total_sum
      context['cost']=cost+marja1

      return context



class Money_Create(LoginRequiredMixin,TemplateView):
   template_name = 'create_money.html'
   login_url = reverse_lazy('login')

   def post(self, request, *args, **kwargs):
      name=request.POST.get('category')
      sum=request.POST.get('amount')
      Finance.objects.create(
         name=name,
         sum=sum
      )
      return redirect('money')



class Debt(LoginRequiredMixin,TemplateView):
   template_name = 'debt.html'
   login_url = reverse_lazy('login')


   def post(self, request, *args, **kwargs):
      pk=request.POST.get('pk')
      action = request.POST.get('action')

      if action == "update":
         payment_data = request.POST.get('payment_data')
         Orders.objects.filter(pk=pk).update(payment_data=payment_data)
      elif action == "payment":
         Orders.objects.filter(pk=pk).update(stage='finished',complete_date=now().date())
         mess(pk)



      return JsonResponse({'status': 'success'})



   def get_context_data(self, *, object_list=None, **kwargs):
      context = super().get_context_data(**kwargs)
      search=self.request.GET.get("search")

      query=Orders.objects.filter(stage='order_ready')
      if search:
         query=query.filter(client__icontains=search)
      #context['total_sum']=query.aggregate(total_sum=Sum(F('order_sum') - F('order_predoplata')))['total_sum'] or 0
     # context['order']=query.values('client','complete_order','phone','payment_data','pk').annotate(dolg=F('order_sum') - F('order_predoplata'))
      #print(query.values('phone').annotate(sum=Sum('order_sum')))

      return context




class WarehouseView(LoginRequiredMixin, TemplateView):
   template_name = 'warehouse.html'
   login_url = reverse_lazy('login')

   def get_context_data(self, *, object_list=None, **kwargs):
      context = super().get_context_data(**kwargs)
      search = self.request.GET.get('search')
      limit_subquery = WarehouseLimit.objects.filter(product=OuterRef('product')).order_by('-id').values('limit')[:1]
      stock_subquery = Consumables.objects.filter(add=OuterRef('product')).values('add').annotate(sum=Sum('quantity')).values('sum')[:1]
      if search:
         context['warehouse'] = Warehouse.objects.filter(product__icontains=search).values('product').annotate(
            last_added=Max('created_at'), limit=Subquery(limit_subquery), quantity=Sum('quantity'),
            stock=F('quantity') - Subquery(stock_subquery))
      else:
         context['warehouse'] = Warehouse.objects.values('product').annotate(
            last_added=Max('created_at'), limit=Subquery(limit_subquery), quantity=Sum('quantity'),
            stock=F('quantity') - Subquery(stock_subquery))




      return context


class WarehouseCreateView(LoginRequiredMixin, TemplateView):
   template_name = 'warehouse_create.html'
   login_url = reverse_lazy('login')


   def post(self, request, *args, **kwargs):
      city=request.POST.get('city')
      category = request.POST.get('category')
      product = request.POST.get('product')
      quantity = request.POST.get('quantity')
      deliver = request.POST.get('deliver')
      created_at = request.POST.get('created_at')
      Warehouse.objects.create(city=city,category=category,product=product,quantity=quantity,deliver=deliver,created_at=created_at)

      return redirect('warehouse')




class WarehouseLimitView(LoginRequiredMixin, TemplateView):
   template_name = 'warehouse_limit.html'
   login_url = reverse_lazy('login')

   def post(self, request, *args, **kwargs):
      category = request.POST.get('category')
      product = request.POST.get('product')
      limit = request.POST.get('limit')
      WarehouseLimit.objects.create(category=category,product=product,limit=limit)

      return redirect('warehouse')

