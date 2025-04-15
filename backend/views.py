from django.shortcuts import render,redirect
from django.http import HttpResponse
from django.views.generic import View,TemplateView,DetailView,UpdateView
from .models import Profile,Rezident,Finance,Warehouse,WarehouseLimit,Consumables,Orders
from django.contrib.auth.models import User
from django.urls import reverse_lazy
from django.contrib.auth import authenticate,login,logout
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Sum,Q,Count,F,Max,Prefetch,OuterRef, Subquery
from django.utils.timezone import now
from django.http import JsonResponse

class Dashboard(LoginRequiredMixin,TemplateView):
   login_url = reverse_lazy('login')
   template_name = 'dashboard.html'




   def post(self,request):
      action=request.POST.get('action')
      pk = request.POST.get('pk')
      stage=request.POST.get('stage')

      if action == "designer":
         Orders.objects.filter(pk=pk).update(stage="technologist")
         return redirect(request.path)
      elif action == "technologist":
         add = request.POST.getlist('add')
         price = request.POST.getlist('price')
         catigories = request.POST.getlist('catigories')
         # rezka=request.POST.get('rezka')
         # svarka = request.POST.get('svarka')
         # fill = request.POST.get('fill')
         # pechat = request.POST.get('print')
         Orders.objects.filter(pk=pk).update(stage="manufacturing")
         consumables = [
            Consumables(order_id=pk, add=a, price=p, catigories=c)
            for a, p, c in zip(add, price, catigories)
         ]
         Consumables.objects.bulk_create(consumables)

         return redirect(request.path)
      elif action == "delivery":
         photo = request.FILES.get('photo')
         order=Orders.objects.filter(pk=pk).first()
         order.stage="order_ready"
         order.delivery_photo=photo
         order.save(update_fields=['stage','delivery_photo'])

         return redirect(request.path)

      elif action == "admin":
         Orders.objects.filter(pk=pk).update(stage=stage)
         return JsonResponse({'status': 'success'})
      return JsonResponse({'status': 'error', 'message': 'Invalid action'}, status=400)





   def get_context_data(self, *, object_list=None, **kwargs):
      context = super().get_context_data(**kwargs)
      search = self.request.GET.get('search')

      stages = [
         'accepted', 'design', 'technologist', 'manufacturing',
         'assembly', 'delivery', 'order_ready', 'finished'
      ]

      for stage in stages:
         queryset = Orders.objects.filter(stage=stage)

         # Add search filter if present
         if search:
            queryset = queryset.filter(client__icontains=search)

         # Add prefetch for 'design' stage
         if stage == 'design':
            queryset = queryset.prefetch_related('consumables')

         context[stage] = queryset

      return context



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
      if 'delivery_photo' in request.FILES:
         self.object.delivery_photo = request.FILES.get('delivery_photo')

      # Save the updated order
      self.object.save()

      # Handle Consumables data
      add = request.POST.getlist('add')
      price = request.POST.getlist('price')
      catigories = request.POST.getlist('catigories')

      # Delete old consumables for this order to avoid duplication
      Consumables.objects.filter(order=self.object).delete()

      # Create new consumables
      consumables = [
         Consumables(order=self.object, add=a, price=p, catigories=c)
         for a, p, c in zip(add, price, catigories)
      ]
      Consumables.objects.bulk_create(consumables)

      # Redirect after successful update
      return redirect('dashboard')



class Order(LoginRequiredMixin,TemplateView):
   template_name = 'order.html'
   login_url = reverse_lazy('login')


   def post(self,request):
      add=request.POST.getlist('add')
      price=request.POST.getlist('price')
      catigories = request.POST.getlist('catigories')



      client = request.POST.get('client')
      adress= request.POST.get('adress')
      order_sum = request.POST.get('order_sum')
      order_predoplata = request.POST.get('order_predoplata')
      description = request.POST.get('description')
      phone = request.POST.get('phone')
      social = request.POST.get('social')
      stage = request.POST.get('stage')
      add_order = request.POST.get('add_order')
      complete_order = request.POST.get('complete_order')


      order=Orders.objects.create\
         (client=client,
          adress=adress,
          order_sum=order_sum,
          order_predoplata=order_predoplata,
          description=description,
          phone=phone,
          social=social,
          stage=stage,
          add_order=add_order,
          complete_order=complete_order)
      consumables = [
         Consumables(order=order, add=a, price=p, catigories=c)
         for a, p, c in zip(add, price, catigories)
      ]
      Consumables.objects.bulk_create(consumables)

      return redirect('dashboard')



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

      context['profile']=Profile.objects.filter(approve=False)

      return context


class Staff(LoginRequiredMixin,TemplateView):
   template_name = 'staff.html'
   login_url = reverse_lazy('login')





   def get_context_data(self, *, object_list=None, **kwargs):
      context = super().get_context_data(**kwargs)
      search=self.request.GET.get('search')

      if search:
         # Apply a case-insensitive search across multiple fields
         context['profile'] = Profile.objects.filter(
            approve=True
         ).filter(
            Q(name__icontains=search) |
            Q(lastname__icontains=search) |
            Q(middle_name__icontains=search)  # Add more fields as necessary
         )
      else:
         # Return all profiles if no search term is provided
         context['profile'] = Profile.objects.filter(approve=True)




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







class Money(LoginRequiredMixin,TemplateView):
   template_name = 'money.html'
   login_url = reverse_lazy('login')

   def get_context_data(self, *, object_list=None, **kwargs):
      context = super().get_context_data(**kwargs)
      first = self.request.GET.get('first')
      second=self.request.GET.get('second')
      today = now()
      query=Finance.objects.filter(
          created_at__year=today.year,
          created_at__month=today.month
      )

      order = Orders.objects.filter(stage="finished", complete_order__year=today.year,
                                    complete_order__month=today.month)

      if first and second:
         query = query.filter(created_at__range=(first, second))
         order=order.filter(complete_order__range=(first,second))

      marja=Consumables.objects.filter(order__in=order).aggregate(total_sum=Sum('price'))['total_sum'] or 0
      total_sum=order.aggregate(total_sum=Sum('order_sum'))['total_sum'] or 0
      context['marja']=total_sum - marja
      context['money'] = query
      context['count']=order.count()
      context['total_sum']=total_sum
      context['cost']=query.aggregate(total_sum=Sum('sum'))['total_sum'] or 0

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



   def get_context_data(self, *, object_list=None, **kwargs):
      context = super().get_context_data(**kwargs)


      return context




class WarehouseView(LoginRequiredMixin, TemplateView):
   template_name = 'warehouse.html'
   login_url = reverse_lazy('login')

   def get_context_data(self, *, object_list=None, **kwargs):
      context = super().get_context_data(**kwargs)
      search = self.request.GET.get('search')
      limit_subquery = WarehouseLimit.objects.filter(product=OuterRef('product')).order_by('-id').values('limit')[:1]
      stock_subquery = Consumables.objects.filter(add=OuterRef('product')).values('add').annotate(count=Count('id')).values('count')[:1]
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

