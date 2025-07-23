import time
from django.db import connection, reset_queries
from django.http import JsonResponse
from django.db.models import Prefetch

from django.shortcuts import render,redirect
from django.http import HttpResponse
from django.views.generic import View,TemplateView,DetailView,UpdateView
from .models import Profile,Rezident,Finance,Warehouse,WarehouseLimit,Consumables,Orders,Delivery_Photo,Compelete_Photo,Telegram_users,Clients,Social_clients,OrderStaff,Provider,Notification,Manager_Photo
from django.contrib.auth.models import User
from django.urls import reverse_lazy
from django.contrib.auth import authenticate,login,logout
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Sum,Q,Count,F,Max,Prefetch,OuterRef, Subquery,Value,Exists
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



def search_profiles(request):
    position = request.GET.get("position", "")

    qs = Profile.objects.filter(position=position)
    results = [
        {
            "id": profile.id,
            "full_name": f"{profile.lastname} {profile.name}"
        }
        for profile in qs
    ]

    return JsonResponse(results, safe=False)


def assign_project(request):
    if request.method == "POST":
       id=request.POST.get('project_id')
       profile_id = request.POST.get('profile_id')
       action=request.POST.get('action')
       rezka = svarka = fill = print_stage = sborka = 'no'
       if request.POST.get('rezka') == 'true':
          rezka = 'chief'
       if request.POST.get('svarka') == 'true':
          svarka = 'chief'
       if request.POST.get('fill') == 'true':
          fill = 'chief'
       if request.POST.get('print') == 'true':
          print_stage = 'chief'
       if request.POST.get('sborka') == 'true':
          sborka = 'chief'

          # Now update the corresponding order_staff object or create a new one
       OrderStaff.objects.get_or_create(
          order_id=id,
          profile_id=profile_id,
          rezka=rezka,
          svarka=svarka,
          fill=fill,
          print=print_stage,
          sborka=sborka
       )

       return JsonResponse({"status": "ok"})


    else:

       try:
          OrderStaff.objects.get_or_create(order_id=id, profile_id=profile_id)
          return JsonResponse({"status": "ok"})

       except Exception as e:
          return JsonResponse({"error": str(e)}, status=400)










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

class NotificationVIew(LoginRequiredMixin,DetailView):
   login_url = reverse_lazy('login')
   template_name = 'notification.html'
   model = Notification
   context_object_name = 'item'



   def post(self,request,*args, **kwargs):
      action=request.POST.get('action')
      message=request.POST.get('message')
      pk=request.POST.get('pk')
      if action == 'call_center_back':
         Orders.objects.filter(pk=pk).update(stage='call_center')
         Notification.objects.create(order_id=pk,stage=action,message=message)

      elif action == 'fail':
         fail=request.POST.get('fail')
         Orders.objects.filter(pk=pk).update(stage='failed',fail=fail,by_who_fail='менеджером')

      elif action == 'manager':
         staff_pk=request.POST.get('staff_pk')
         if staff_pk:
            Notification.objects.create(order_id=pk,stage='manager_qa',profile_id=staff_pk)

      elif action == 'manager_qa':
         message=request.POST.get('message')
         if message == 'approve':
            Notification.objects.create(order_id=pk, stage='manager_qa_back', profile_id=request.POST.get('staff_pk'),message=message)
         else:
            Notification.objects.create(order_id=pk, stage='manager_qa_back',profile_id=request.POST.get('staff_pk'), message=message)







      return redirect('dashboard')
   def get_queryset(self):
      return super().get_queryset().select_related(
         'order',
         'order__marketing',
         'order__client'
      )
   def get_context_data(self, *, object_list=None, **kwargs):
      context = super().get_context_data(**kwargs)
      notify=self.object
      notify.is_read=True
      notify.save()
      return context
class Dashboard(LoginRequiredMixin,TemplateView):
   login_url = reverse_lazy('login')
   template_name = 'dashboard.html'




   def post(self,request):
      action=request.POST.get('action')
      pk = request.POST.get('pk')
      stage=request.POST.get('stage')


      if action == "admin":
         if stage == "finished":
            Orders.objects.filter(pk=pk).update(stage=stage, complete_date=now().date())

         elif stage == 'delivery':
            Orders.objects.filter(pk=pk).update(stage=stage)
           # admin_tech(pk)

         elif stage == 'design':
            order=Orders.objects.filter(pk=pk).first()
            if order.check_design:
               order.stage=stage
               order.save(update_fields=['stage'])
               Notification.objects.create(stage=stage,order=order)
            else:
               order.stage = 'technologist'
               order.save(update_fields=['stage'])
               Notification.objects.create(stage='technologist', order=order)

            return JsonResponse({'status': 'success', 'reload': True})
         else:
            Orders.objects.filter(pk=pk).update(stage=stage)


         #mess(pk)





         return JsonResponse({'status': 'success'})
      return JsonResponse({'status': 'error', 'message': 'Invalid action'}, status=400)



      # if action == "designer":
      #    Orders.objects.filter(pk=pk).update(stage="technologist")
      #    mess(pk)
      #
      #    return redirect(request.path)
      # elif action == "technologist":
      #    add = request.POST.getlist('add')
      #    quantity=request.POST.getlist('quantity')
      #    rezka = request.POST.get('rezka') == 'on'
      #    svarka = request.POST.get('svarka') == 'on'
      #    fill = request.POST.get('fill') == 'on'
      #    pechat = request.POST.get('print') == 'on'
      #
      #    if rezka:
      #       pod_stage="rezka"
      #    elif svarka:
      #       pod_stage="svarka"
      #    elif fill:
      #       pod_stage="fill"
      #    elif pechat:
      #       pod_stage="print"
      #
      #
      #    Orders.objects.filter(pk=pk).update(stage="manufacturing",stage_pod=pod_stage,rezka=rezka,svarka=svarka,fill=fill,print=pechat)
      #    consumables = [
      #       Consumables(order_id=pk, add=a, price=p, catigories=c, quantity=d)
      #       for a, p, c, d in zip(add, price, catigories, quantity)
      #    ]
      #    Consumables.objects.bulk_create(consumables)
      #
      #    mess(pk)
      #
      #    return redirect(request.path)
      # elif action == "delivery":
      #    photo = request.FILES.getlist('photo')
      #
      #    order=Orders.objects.filter(pk=pk).update(stage='order_ready')
      #    delivery = [
      #       Delivery_Photo(order_id=pk, photo=p)
      #       for p in photo
      #    ]
      #    Delivery_Photo.objects.bulk_create(delivery)
      #
      #
      #    mess(pk)
      #
      #    return redirect(request.path)
      #
      # elif action == 'chief':
      #    stage_pod=request.POST.get('pod_stage')
      #    order=Orders.objects.filter(pk=pk).first()
      #    check=getattr(order,stage_pod,None)
      #
      #
      #    if check is False:
      #       services = []
      #       if order.rezka:
      #          services.append("Резка")
      #       if order.svarka:
      #          services.append("Сварка")
      #       if order.fill:
      #          services.append("Покраска")
      #       if order.print:
      #          services.append("Печать")
      #
      #       x = ", ".join(services)
      #       return JsonResponse({'message': f'Для данного проекта технолог выбрал только этапы: {x}'}, status=401)
      #
      #
      #
      #    if stage_pod:
      #       Orders.objects.filter(pk=pk).update(stage=stage,stage_pod=stage_pod)
      #    else:
      #       if order.full_pay:
      #          Orders.objects.filter(pk=pk).update(stage='delivery')
      #          # admin_tech(pk)
      #       else:
      #          Orders.objects.filter(pk=pk).update(stage=stage)
      #       #mess(pk)
      #
      #
      #
      #
      #    return JsonResponse({'status': 'success'})









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

      context['Notifcation']=Notification.objects.all().order_by('-id')
      return context


class MyProjects(LoginRequiredMixin, TemplateView):
   login_url = reverse_lazy('login')
   template_name = 'my_projects.html'

   def post(self, request, *args, **kwargs):
      action=request.POST.get('action')
      pk=request.POST.get('pk')
      design = request.FILES.get('design')
      description_design = request.POST.get('description_design')
      if action == "designer_add":
         order_staff=OrderStaff.objects.filter(pk=pk).first()
         #order = Orders.objects.filter(pk=pk).first()
         update_fields = []

         if design:
            order_staff.order.design = design
            update_fields.append('design')

         if description_design:
            order_staff.order.description_design = description_design
            update_fields.append('description_design')

         if update_fields:
            order_staff.order.save(update_fields=update_fields)
         order_staff.upload = True
         order_staff.save(update_fields=['upload'])



      elif action == 'designer_chief_add':
         order_staff, created=OrderStaff.objects.get_or_create(order_id=pk,profile=request.user.profile)

         update_fields = []

         if design:
            order_staff.order.design = design
            update_fields.append('design')

         if description_design:
            order_staff.order.description_design = description_design
            update_fields.append('description_design')

         if update_fields:
            order_staff.order.save(update_fields=update_fields)

         order_staff.upload = True
         order_staff.save(update_fields=['upload'])

      elif action == 'designer_chief_complete':
         update = request.POST.get('update')
         stage=request.POST.get('stage')

         if update:
            OrderStaff.objects.filter(profile=request.user.profile,order_id=pk).update(complete=True)
         else:
            OrderStaff.objects.create(profile=request.user.profile, complete=True, order_id=pk)
         Orders.objects.filter(pk=pk).update(stage='technologist')
         Notification.objects.create(stage='technologist', order_id=pk)

      elif action == 'technology_add':
         add = request.POST.getlist('add')
         rezka = request.POST.get('rezka') == 'on'
         svarka = request.POST.get('svarka') == 'on'
         fill = request.POST.get('fill') == 'on'
         pechat = request.POST.get('print') == 'on'
         quantity = request.POST.getlist('quantity')
         if rezka:
            pod_stage = "rezka"
         elif svarka:
            pod_stage = "svarka"
         elif fill:
            pod_stage = "fill"
         elif pechat:
            pod_stage = "print"

         order_staff = OrderStaff.objects.filter(pk=pk).first()
         order_pk=order_staff.order.pk
         Orders.objects.filter(pk=order_pk).update(stage_pod=pod_stage, rezka=rezka, svarka=svarka,
                                             fill=fill, print=pechat)
         consumables = [
            Consumables(order_id=order_pk, add=a, quantity=d)
            for a, d in zip(add,quantity)
         ]
         Consumables.objects.bulk_create(consumables)

         order_staff.upload = True
         order_staff.save(update_fields=['upload'])
      elif action == 'technology_chief_complete':
         photo=request.FILES.getlist('photo')
         message=request.POST.get('message')
         Orders.objects.filter(pk=pk).update(stage='manager_2')
         notification=Notification.objects.create(stage='manager_2',order_id=pk,message=message)
         photo = request.FILES.getlist('photo')

         delivery = [
            Manager_Photo(notification=notification, photo=p)
            for p in photo
         ]
         Manager_Photo.objects.bulk_create(delivery)

      elif action == 'technology_chief_add':
         add = request.POST.getlist('add')
         rezka = request.POST.get('rezka') == 'on'
         svarka = request.POST.get('svarka') == 'on'
         fill = request.POST.get('fill') == 'on'
         pechat = request.POST.get('print') == 'on'
         quantity = request.POST.getlist('quantity')
         if rezka:
            pod_stage = "rezka"
         elif svarka:
            pod_stage = "svarka"
         elif fill:
            pod_stage = "fill"
         elif pechat:
            pod_stage = "print"

         order_staff = OrderStaff.objects.get_or_create(order_id=pk,profile=request.user.profile,upload=True)
         order_pk=pk
         Orders.objects.filter(pk=order_pk).update(stage_pod=pod_stage, rezka=rezka, svarka=svarka,
                                             fill=fill, print=pechat)
         consumables = [
            Consumables(order_id=order_pk, add=a, quantity=d)
            for a, d in zip(add,quantity)
         ]
         Consumables.objects.bulk_create(consumables)

      elif action == 'staff_complete':
         OrderStaff.objects.filter(pk=pk).update(complete=True)
         order=OrderStaff.objects.filter(pk=pk).first()
         Notification.objects.create(profile=request.user.profile,stage=order.order.stage,order=order.order)


      elif action == 'warehouse':
         order_staff=OrderStaff.objects.create(profile=request.user.profile,order_id=pk,complete=True)
         Consumables.objects.filter(order_id=pk).update(warehouse=True)
         Orders.objects.filter(pk=pk).update(stage='manufacturing')


      elif action == 'account':
         payment=request.POST.get('payment')
         stage = request.POST.get('stage')

         if payment:
            Orders.objects.filter(pk=pk).update(stage=stage,full_pay=True)

         else:
            Orders.objects.filter(pk=pk).update(stage=stage)

      elif action =='delivery':

       order_staff,created=OrderStaff.objects.get_or_create(order_id=pk,profile=request.user.profile)
       Orders.objects.filter(pk=pk).update(stage='installation')
       order_staff.complete = True
       order_staff.save(update_fields=['complete'])

      elif action == 'installer':
         order_staff, created = OrderStaff.objects.get_or_create(order_id=pk, profile=request.user.profile)
         if order_staff.upload:
            Orders.objects.filter(pk=pk).update(stage='quality_control')
            order_staff.complete = True
            order_staff.save(update_fields=['complete'])


         else:
            photo = request.FILES.getlist('photo')

            delivery = [
               Delivery_Photo(order_id=pk, photo=p)
               for p in photo
            ]
            Delivery_Photo.objects.bulk_create(delivery)
            if photo:
               order_staff.upload = True
               order_staff.save(update_fields=['upload'])

      elif action == 'chief_staff':
         rezka = request.POST.get('rezka') == 'on'
         svarka = request.POST.get('svarka') == 'on'
         fill = request.POST.get('fill') == 'on'
         pechat = request.POST.get('print') == 'on'
         sborka = request.POST.get('sborka') == 'on'

         order_staff = OrderStaff.objects.filter(order_id=pk, profile=request.user.profile).first()
         stages=[]

         check_stages = []
         for stage in ['rezka', 'svarka', 'fill', 'print', 'sborka']:
            if getattr(order_staff.order, stage):
               check_stages.append(stage)








         if rezka:
            order_staff.rezka='staff'
            check_stages.remove('rezka')

         elif  order_staff.order.stage_pod in ['svarka', 'fill', 'print', 'sborka'] and 'rezka' in check_stages:
            check_stages.remove('rezka')

         if svarka:
            check_stages.remove('svarka')
            order_staff.svarka = 'staff'

         elif order_staff.order.stage_pod in [ 'fill', 'print', 'sborka'] and 'svarka' in check_stages:
            check_stages.remove('svarka')


         if fill:

            check_stages.remove('fill')
            order_staff.fill = 'staff'

         elif order_staff.order.stage_pod in ['print', 'sborka'] and 'fill' in check_stages:
            check_stages.remove('fill')

         if pechat:
            check_stages.remove('print')
            order_staff.print = 'staff'

         elif  order_staff.order.stage_pod in [ 'sborka'] and 'print' in check_stages:
            check_stages.remove('print')
         if sborka:
            check_stages.remove('sborka')
            order_staff.sborka = 'staff'



         if check_stages:
            order_staff.order.stage_pod = check_stages[0]

         else:
            order_staff.order.stage_pod='ready'






         order_staff.order.save(update_fields=['stage_pod'])
         order_staff.save()

      elif action == 'chief_staff_complete':
         orderstaff=OrderStaff.objects.filter(pk=pk).first()

         if orderstaff.sborka == 'staff':
            orderstaff.order.stage_pod='ready'
            orderstaff.order.save(update_fields=['stage_pod'])

         orderstaff.complete=True
         orderstaff.save()

      elif action == 'qa_chief':
         order=Orders.objects.filter(pk=pk).update(stage='finished')
         #OrderStaff.objects.create(order=order,profile=request.user.profile,complete=True)














      return redirect(request.path)
   def get_context_data(self, *, object_list=None, **kwargs):
      context = super().get_context_data(**kwargs)
      profile=self.request.user.profile
      is_uploaded_by_chief = OrderStaff.objects.filter(
         order=OuterRef('pk'),
         profile=profile,
         upload=True
      )


      context['technologist_cheif'] = Orders.objects.annotate(
    uploaded_by_chief=Exists(is_uploaded_by_chief)
   ).filter(stage='technologist').prefetch_related(
    Prefetch(
        'order_staff',
        queryset=OrderStaff.objects.filter(profile__position='technologist').select_related('profile'),
        to_attr='designer_staff'
    )
)



      context['designer_cheif']= Orders.objects.annotate(
    uploaded_by_chief=Exists(is_uploaded_by_chief)
   ).filter(stage='design').prefetch_related(
    Prefetch(
        'order_staff',
        queryset=OrderStaff.objects.filter(profile__position='designer').select_related('profile'),
        to_attr='designer_staff'
    )
)

      context['designer'] = OrderStaff.objects.filter(profile=profile,order__stage='design',complete=False).select_related('order')
      context['technologist'] = OrderStaff.objects.filter(profile=profile, order__stage='technologist',
                                                      complete=False).select_related('order')

      context['warehouse']=Orders.objects.filter(stage='warehouse')
      context['account']=Orders.objects.filter(stage__in=['accounting', 'accounting_2']).select_related('client')

      context['delivery_cheif']= Orders.objects.annotate(
    uploaded_by_chief=Exists(is_uploaded_by_chief)
   ).filter(stage='delivery').prefetch_related(
    Prefetch(
        'order_staff',
        queryset=OrderStaff.objects.filter(profile__position='delivery').select_related('profile'),
        to_attr='designer_staff'
    )
)
      context['chief_staff'] = OrderStaff.objects.filter(profile=profile, order__stage='manufacturing',
                                                          complete=False).select_related('order')

      context['delivery'] = OrderStaff.objects.filter(profile=profile, order__stage='delivery',
                                                      complete=False).select_related('order')

      context['installer_chief']=Orders.objects.annotate(uploaded_by_chief=Exists(is_uploaded_by_chief)).filter(stage='installation').prefetch_related(
    Prefetch(
        'order_staff',
        queryset=OrderStaff.objects.filter(profile__position='installer').select_related('profile'),
        to_attr='designer_staff'
    ))
      context['installer'] = OrderStaff.objects.filter(profile=profile, order__stage='installation',
                                                      complete=False).select_related('order')

      context['manufacturing'] = Orders.objects.filter(
         stage='manufacturing').prefetch_related(
         Prefetch(
            'order_staff',
            queryset=OrderStaff.objects.filter(profile__position='chief_staff').select_related('profile'),
            to_attr='designer_staff'
         ))
      context['quality_control'] = Orders.objects.filter(
         stage='quality_control').prefetch_related(
         Prefetch(
            'order_staff',
            queryset=OrderStaff.objects.filter(profile__position='qa_staff').select_related('profile'),
            to_attr='designer_staff'
         ))
      context['accounting_or_delivery']=Orders.objects.filter(stage__in=['accounting_2','delivery'])
      context['rezka'] = [o for o in context['manufacturing'] if o.stage_pod == 'rezka']
      context['svarka'] = [o for o in context['manufacturing'] if o.stage_pod == 'svarka']
      context['fill'] = [o for o in context['manufacturing'] if o.stage_pod == 'fill']
      context['print'] = [o for o in context['manufacturing'] if o.stage_pod == 'print']
      context['sborka'] = [o for o in context['manufacturing'] if o.stage_pod == 'sborka']
      context['ready'] = [o for o in context['manufacturing'] if o.stage_pod == 'ready']

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
      obj = self.get_object()
      action = request.POST.get('action')
      if action == 'delete':
         obj.delete()
         return redirect('dashboard')
      vstrecha = request.POST.get('vstrecha')
      zayavki = request.POST.get('zayavka')
      order_name = request.POST.get('order_name')
      order_sum = request.POST.get('order_sum') or 0
      catigories = request.POST.get('catigories')
      order_predoplata = request.POST.get('order_predoplata') or 0
      tz = request.FILES.get('tz')
      check_design = request.POST.get('check_design') == 'on'
      design = request.FILES.get('design')
      latitude = request.POST.get('latitude') or 0
      longitude = request.POST.get('longitude') or 0
      razmer = request.POST.get('razmer')
      description = request.POST.get('description')
      description_design = request.POST.get('description_design')

      add_order = request.POST.get('add_order') or None
      complete_order = request.POST.get('complete_order') or None
      phone = request.POST.get('phone')
      social = request.POST.get('social')

      if action == 'INDIVIDUAL':
         name = request.POST.get('name')
         lastname = request.POST.get('lastname')
         middle_name = request.POST.get('middle_name')
         obj.client.adress = None
         obj.client.inn = None
         obj.client.account = None
         obj.client.phone = phone
         obj.client.company_name = None
         obj.client.name = name
         obj.client.lastname = lastname
         obj.client.middle_name = middle_name
         obj.client.phone = phone
         obj.client.client_type = "INDIVIDUAL"
         obj.client.active = True
         obj.client.save()

      else:
         adress = request.POST.get('adress')
         company_name = request.POST.get('company_name')
         inn = request.POST.get('inn') or None
         account = request.POST.get('account') or None
         mfo = request.POST.get('mfo') or None

         obj.client.name = None
         obj.client.lastname = None
         obj.client.middle_name = None
         obj.client.company_name = company_name
         obj.client.adress = adress
         obj.client.inn = inn
         obj.client.account = account
         obj.client.phone = phone
         obj.client.client_type = "LEGAL_ENTITY"
         obj.client.active=True
         obj.client.save()

      obj.order_name = order_name
      obj.zayavki = zayavki
      obj.vstrecha = vstrecha
      obj.order_sum = order_sum
      obj.order_predoplata = order_predoplata
      obj.description = description
      obj.catigories = catigories
      obj.tz = tz
      obj.check_design = check_design
      obj.design = design
      obj.latitude = latitude
      obj.longitude = longitude
      obj.razmer = razmer
      obj.description_design = description_design
      obj.add_order = add_order
      obj.complete_order = complete_order

      obj.save()
      #mess(self.object.pk)

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
      latitude = request.POST.get('latitude') or 0
      longitude = request.POST.get('longitude') or 0
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

class FinanceProfileView(LoginRequiredMixin,TemplateView):
   template_name = 'finance_profile.html'
   login_url = reverse_lazy('login')
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
      who = request.POST.get('who')
      salary_pure = request.POST.get('salary_pure') or 0
      salary_black = request.POST.get('salary_black') or 0
      if action == "approve" and who =='manager':
         Profile.objects.filter(id=pk).update(approve=True)
      elif action == 'approve' and who == 'admin':
         Profile.objects.filter(id=pk).update(approve=True,salary_pure=salary_pure,salary_black=salary_black)
      elif action == 'approve' and who == 'account':

         Profile.objects.filter(id=pk).update(approve_accounting=True,salary_pure=salary_pure,salary_black=salary_black)
      elif action == 'reject':
         User.objects.filter(profile__id=pk).delete()
         #Profile.objects.filter(id=pk).delete()


      return redirect(request.path)







   def get_context_data(self, *, object_list=None, **kwargs):
      context = super().get_context_data(**kwargs)

      context['profile']=Profile.objects.filter(approve=False).order_by('-id')
      context['account'] = Profile.objects.filter(approve=True,approve_accounting=False).order_by('-id')
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

class ProviderView(LoginRequiredMixin,TemplateView):
   template_name = 'provider.html'
   login_url = reverse_lazy('login')


   def get_context_data(self, *, object_list=None, **kwargs):
      context = super().get_context_data(**kwargs)
      search = self.request.GET.get('search')
      profile=self.request.user.profile

      if search:
         context['profile'] = Provider.objects.filter(Q(name__icontains=search) |
        Q(lastname__icontains=search) |
        Q(middle_name__icontains=search))
      else:
         context['profile'] = Provider.objects.all()

      return context


class ProvideCreateView(LoginRequiredMixin,TemplateView):
   template_name = 'provider_add.html'
   login_url = reverse_lazy('login')


   def post(self, request, *args, **kwargs):
      name = request.POST.get('name')
      lastname = request.POST.get('lastname')
      middle_name = request.POST.get('middle_name')
      phone = request.POST.get('phone')
      Provider.objects.create(name=name,lastname=lastname,middle_name=middle_name,phone=phone)





      return redirect('provider')
class MarketingClietView(LoginRequiredMixin,TemplateView):
   template_name = 'marketing.html'
   login_url = reverse_lazy('login')



   def post(self, request, *args, **kwargs):
      pk = request.POST.get('pk')
      order = Orders.objects.filter(marketing__id=pk).first()
      if order:
         order.stage = 'call_center'
         order.save(update_fields=['stage'])
         Notification.objects.create(order=order, stage='call_center')
      return redirect(request.path)


   def get_context_data(self, *, object_list=None, **kwargs):
      context = super().get_context_data(**kwargs)
      search = self.request.GET.get('search')
      profile=self.request.user.profile

      if search:
         context['profile'] = Social_clients.objects.filter(profile=profile,order__stage='marketing',client_name__icontains=search).select_related('order').exclude(order__stage='failed')
      else:
         context['profile'] = Social_clients.objects.filter(profile=profile,order__stage='marketing').select_related('order').exclude(order__stage='failed')

      return context



class ArchiveOrder(LoginRequiredMixin,TemplateView):
   template_name = 'archive.html'
   login_url = reverse_lazy('login')



   def get_context_data(self, *, object_list=None, **kwargs):
      context = super().get_context_data(**kwargs)
      context['failed']=Orders.objects.filter(stage='failed').order_by('-fail_date')
      context['finished'] = Orders.objects.filter(stage='archive').order_by('-complete_date')
      return context

class Call_center(LoginRequiredMixin,TemplateView):
   template_name = 'call_center.html'
   login_url = reverse_lazy('login')



   def post(self, request, *args, **kwargs):
      pk = request.POST.get('pk')
      Orders.objects.filter(id=pk).update(stage='manager')
      Notification.objects.create(order_id=pk,stage='manager')
      return redirect(request.path)

   def get_context_data(self, *, object_list=None, **kwargs):
      context = super().get_context_data(**kwargs)
      context['order']=Orders.objects.filter(stage='call_center')
      search = self.request.GET.get('search')

      if search:
         context['order'] = Orders.objects.filter(
    Q(stage='call_center') &
      ( Q(client__name__icontains=search) |
        Q(client__company_name__icontains=search) |
        Q(marketing__client_name__icontains=search)
    )
).select_related('client','marketing')

      else:
         context['order'] = Orders.objects.filter(stage='call_center').select_related('client','marketing')
      return context
class Call_center_add(LoginRequiredMixin,TemplateView):
   template_name = 'call_center_add.html'
   login_url = reverse_lazy('login')


   def post(self,request,*args, **kwargs):


      action = request.POST.get('action')
      vstrecha=request.POST.get('vstrecha')
      zayavki = request.POST.get('zayavka')
      order_name=request.POST.get('order_name')
      order_sum = request.POST.get('order_sum') or 0
      catigories=request.POST.get('catigories')
      order_predoplata = request.POST.get('order_predoplata') or 0
      tz=request.FILES.get('tz')
      check_design=request.POST.get('check_design') == 'on'
      design = request.FILES.get('design')
      latitude=request.POST.get('latitude' ) or 0
      longitude=request.POST.get('longitude') or 0
      razmer=request.POST.get('razmer')
      description = request.POST.get('description')
      description_design=request.POST.get('description_design')

      add_order = request.POST.get('add_order') or None
      complete_order = request.POST.get('complete_order') or None
      phone=request.POST.get('phone')
      social = request.POST.get('social')



      if action == 'INDIVIDUAL':
         name = request.POST.get('name')
         lastname = request.POST.get('lastname')
         middle_name = request.POST.get('middle_name')
         client=Clients.objects.create(name=name, lastname=lastname, middle_name=middle_name, social=social, phone=phone,
                                client_type=action)
      else:
         adress = request.POST.get('adress')
         company_name = request.POST.get('company_name')
         inn = request.POST.get('inn') or None
         account = request.POST.get('account') or None
         mfo = request.POST.get('mfo') or None
         client=Clients.objects.create(adress=adress, company_name=company_name, inn=inn, social=social, phone=phone,
                                client_type='LEGAL_ENTITY', account=account, mfo=mfo)




      order = Orders.objects.create \
         (client=client,
          call_center=request.user.profile,
          order_name=order_name,
          zayavki=zayavki,
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
          stage='call_center',
          add_order=add_order,
          complete_order=complete_order

          )


      return redirect('call_center')




class DetailCall(LoginRequiredMixin,DetailView):
   model = Orders
   login_url = reverse_lazy('login')
   template_name = 'call_center_detail.html'
   context_object_name = 'item'

   def post(self, request, *args, **kwargs):
      action = request.POST.get('action')

      obj = self.get_object()
      if action == 'delete':
         obj.delete()
      else:
         vstrecha = request.POST.get('vstrecha')
         zayavki = request.POST.get('zayavka')
         order_name = request.POST.get('order_name')
         order_sum = request.POST.get('order_sum') or 0
         catigories = request.POST.get('catigories')
         order_predoplata = request.POST.get('order_predoplata') or 0
         tz = request.FILES.get('tz')
         check_design = request.POST.get('check_design') == 'on'
         design = request.FILES.get('design')
         latitude = request.POST.get('latitude') or 0
         longitude = request.POST.get('longitude') or 0
         razmer = request.POST.get('razmer')
         description = request.POST.get('description')
         description_design = request.POST.get('description_design')

         add_order = request.POST.get('add_order') or None
         complete_order = request.POST.get('complete_order') or None
         phone = request.POST.get('phone')
         social = request.POST.get('social')

         if action == 'INDIVIDUAL':
            name = request.POST.get('name')
            lastname = request.POST.get('lastname')
            middle_name = request.POST.get('middle_name')
            if obj.client:
               obj.client.phone = phone
               obj.client.name = name
               obj.client.lastname = lastname
               obj.client.middle_name = middle_name
               obj.client.client_type = "INDIVIDUAL"
               obj.client.save()
            else:
               c=Clients.objects.create(phone=phone,name=name,lastname=lastname,middle_name=middle_name,client_type="INDIVIDUAL")
               obj.client=c



         else:
            adress = request.POST.get('adress')
            company_name = request.POST.get('company_name')
            inn = request.POST.get('inn') or None
            account = request.POST.get('account') or None
            mfo = request.POST.get('mfo') or None

            if obj.client:
               obj.client.company_name = company_name
               obj.client.adress = adress
               obj.client.inn = inn
               obj.client.account = account
               obj.client.phone = phone
               obj.client.client_type = "LEGAL_ENTITY"
               obj.client.save()
            else:
               c = Clients.objects.create(company_name=company_name, adress=adress, inn=inn, account=account,
                                          client_type="LEGAL_ENTITY",phone=phone)
               obj.client = c



         obj.order_name = order_name
         obj.zayavki = zayavki
         obj.vstrecha = vstrecha
         obj.order_sum = order_sum
         obj.order_predoplata = order_predoplata
         obj.description = description
         obj.catigories = catigories
         if tz:
            obj.tz = tz

         if design:
            obj.design = design
         obj.check_design = check_design

         obj.latitude = latitude
         obj.longitude = longitude
         obj.razmer = razmer
         obj.description_design = description_design
         obj.add_order = add_order
         obj.complete_order = complete_order

         obj.save()





      return redirect('call_center')



class DetailMarketing(LoginRequiredMixin,DetailView):
   model = Social_clients
   login_url = reverse_lazy('login')
   template_name = 'marketing_detail.html'
   context_object_name = 'item'

   def post(self, request, *args, **kwargs):
      pk=request.POST.get('pk')
      phone = request.POST.get('phone')
      client_name = request.POST.get('client')
      comment = request.POST.get('comment')
      reason=request.POST.get('reason')
      self.object = self.get_object()
      if pk:

         Orders.objects.filter(marketing__id=pk).update(stage='failed',fail=reason,fail_date=now().date(),by_who_fail='соц.маркетологом')
      else:

         self.object.phone = phone
         self.object.client_name = client_name
         self.object.comment = comment
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
      order=Orders.objects.create(stage='marketing')
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


      price_subquery = Warehouse.objects.filter(product=OuterRef('add')).order_by('-id').values('price')[:1]
      marja=Consumables.objects.filter(order__in=order,warehouse=True).aggregate(total_sum=Sum(Subquery(price_subquery)*F('quantity')))['total_sum'] or 0
      marja1 = Consumables.objects.filter(order__in=order1,warehouse=True).aggregate(total_sum=Sum(Subquery(price_subquery) * F('quantity')))[
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
      stock_subquery = Consumables.objects.filter(add=OuterRef('product'),warehouse=True).values('add').annotate(sum=Sum('quantity')).values('sum')[:1]
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
      user_id=request.POST.get('user_id')
      price=request.POST.get('price')
      Warehouse.objects.create(city=city,category=category,product=product,quantity=quantity,provider_id=user_id,created_at=created_at,price=price)

      return redirect('warehouse')

   def get_context_data(self, *, object_list=None, **kwargs):
      context = super().get_context_data(**kwargs)
      context['provider']=Provider.objects.all()
      return context


class WarehouseLimitView(LoginRequiredMixin, TemplateView):
   template_name = 'warehouse_limit.html'
   login_url = reverse_lazy('login')

   def post(self, request, *args, **kwargs):
      category = request.POST.get('category')
      product = request.POST.get('product')
      limit = request.POST.get('limit')
      WarehouseLimit.objects.create(category=category,product=product,limit=limit)

      return redirect('warehouse')

