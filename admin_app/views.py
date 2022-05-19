from re import T
from typing import FrozenSet
from django.db import models
from django.db.models.functions.datetime import ExtractMonth
from django.views.decorators.cache import never_cache
from cart.models import Coupons as Coupon
from orders.views import payment, place_order, status
from orders.models import Order, OrderProduct, Payment
from django.http.response import HttpResponse, JsonResponse
from django.contrib import messages
from .forms import CategoryForm, ProductForm, CouponForm,CatofferForm
from django.shortcuts import get_object_or_404, render, redirect
from ecommerce_app.models import Product, Category
from accounts.models import Account
from django.db.models import Q,Count
from orders.models import Order
import csv
import datetime
import xlwt
from django.template.loader import render_to_string
import tempfile
from weasyprint import HTML
from django.contrib.auth.decorators import login_required,user_passes_test
import calendar
from datetime import date


# Admin dashboard

def admin_home(request):
    Shipped =0
    Placed=0
    Cancelled=0
    Returned=0
    Delivered=0

    if request.session.get('signin') == True:
        income = 0
        orders = Order.objects.all()
        for order in orders:
            income += order.order_total
        
        labels = []
        data = []
        orders=OrderProduct.objects.annotate(month=ExtractMonth('created_at')).values('month').annotate(count=Count('id')).values('month','count')
        labels=['jan','feb','march','april','may','june','july','auguest','september']
        data=[0,0,0,0,0,0,0,0,0]
        for d in orders:
            labels.append(calendar.month_name[d['month']])
            data.append([d['count']])
        labels1 = []
        data1 = []
        
        queryset = OrderProduct.objects.all()
        for i in queryset:
            if i.status == 'Placed':
                Placed += 1
            elif i.status == 'Shipped':
                Shipped += 1
            elif i.status == 'Cancelled':
                Cancelled += 1
            elif i.status == 'Delivered':
                Delivered += 1
            elif i.status == 'Returned':
                Returned += 1

        labels1 = ['Shipped', 'Placed', 'Cancelled','Returned','Delivered']
        data1 = [Shipped,Placed,Cancelled,Returned,Delivered]


        order_count = OrderProduct.objects.count()
        product_count=Product.objects.count()
        cat_count=Category.objects.count()
        user_count = Account.objects.count()

        category = Category.objects.all().order_by('-id')[:5]
        products = Product.objects.all().order_by('-id')[:5]
        orderproducts = OrderProduct.objects.all().order_by('-id')[:5]

        context={
            'cat_count':cat_count,
            'product_count':product_count,
            'order_count': order_count,
            'labels1':labels1,
            'data1':data1,


            'labels':labels,
            'data':data,

            'category':category,
            'products':products,
            'orderproducts':orderproducts,
            'income': income,
            'user_count':user_count

        }
        return render(request, 'admin/admin_home.html', context)
    else:
        return redirect('logincheck')
        
#category offer

# Category Management

def category(request):
    if request.session.get('signin') == True:
        category = Category.objects.all()
        return render(request, 'admin/category.html', {'category': category})
    else:
        return redirect('logincheck')


def add_category(request):
    if request.session.get('signin') == True:
        url = request.META.get('HTTP_REFERER')
        if request.method == 'POST':

            form = CategoryForm(request.POST, request.FILES)
            if form.is_valid():
                form.save()
                return redirect('category')
            else:
                messages.error(request, 'Category already added')
                return redirect('add_category')
        else:

            form = CategoryForm()
            context = {'form': form}
            return render(request, 'admin/add_category.html', context)
    else:
        return redirect('logincheck')


def add_cat(request):
    if request.session.get('signin') == True:
        if request.method == 'POST':

            form = CategoryForm(request.POST, request.FILES)
            if form.is_valid():
                form.save()
                return redirect('add_product')
            else:
                messages.error(request, 'Category already added')
                return redirect('add_category')
        else:
            form = CategoryForm()
            context = {'form': form}
            return render(request, 'admin/add_cat.html', context)
    else:
        return redirect('logincheck')


def delete(request):
    if request.session.get('signin') == True:
        id = request.POST['id']
        Category.objects.filter(id=id).delete()
        return JsonResponse({'success': True})
    else:
        return redirect('logincheck')


def admin_category_update(request, slug):
    if request.session.get('signin') == True:
        category = Category.objects.get(slug=slug)
        if request.method == 'POST':
            form = CategoryForm(request.POST, request.FILES, instance=category)

            if form.is_valid():
                form.save()
                return redirect('category')
        else:
            form = CategoryForm(instance=category)
            return render(request, 'admin/admin_category_update.html', {'category': category, 'form': form})
    else:
        return redirect('logincheck')



# Products  Management

def product_man(request):
    if request.session.get('signin') == True:
        product = Product.objects.all().order_by('-id')
        return render(request, 'admin/product_man.html', {'product': product})
    else:
        return redirect('logincheck')




def add_product(request):
    if request.session.get('signin') == True:
        if request.method == 'POST':

            form = ProductForm(request.POST, request.FILES)
            print(request.FILES)
            if form.is_valid():
                product = form.save()
                if product.offer is not None:
                    product.actual_price = product.price
                    product.price = int(product.actual_price-(product.actual_price*product.offer/100))
                    print(product.price,'price')
                    print(product.actual_price,'actual_price')

                else:
                    product.price = int(product.price)
                form.save()
                return redirect('product_man')
            else:
                return redirect('add_product')
        else:

            form = ProductForm()
            products = Product.objects.all()
            return render(request, 'admin/add_product.html', {'products': products, 'form': form})
    else:
        return redirect('logincheck')



def delete_pro(request):
    if request.session.get('signin') == True:
        id = request.POST['id']
        Product.objects.filter(id=id).delete()
        return JsonResponse({'success': True})
    else:
        return redirect('logincheck')


def product_update(request, slug):
    if request.session.get('signin') == True:
        product = Product.objects.get(slug=slug)
        if request.method == 'POST':
            form = ProductForm(request.POST, request.FILES, instance=product)

            if form.is_valid():
                product = form.save()
                if product.offer is not None:
                    product.actual_price = product.price
                    product.price = int(product.actual_price-(product.actual_price*product.offer/100))
                    print(product.price,'price')
                    print(product.actual_price,'actual_price')

                else:
                    product.price = int(product.price)
                form.save()
                return redirect('product_man')
            else:
                return redirect('product_update' ,slug=slug)
        else:
            form = ProductForm(instance=product)
            return render(request, 'admin/product_update.html', {'product': product, 'form': form})
    else:
        return redirect('logincheck')


# User Management

def user_man(request):
    if request.session.get('signin') == True:
        users = Account.objects.filter()
        return render(request, 'admin/user.html', {'users': users})
    else:
        return redirect('logincheck')





def unblock_user(request,):
    if request.session.get('signin') == True:
        id = request.POST['id']
        user = Account.objects.get(id=id)
        user.is_active = True
        user.save()
        return JsonResponse({'success': True})
    else:
        return redirect('logincheck')




def block_user(request):
    if request.session.get('signin') == True:
        id = request.POST['id']
        user = Account.objects.get(id=id)
        user.is_active = False
        user.save()
        return JsonResponse({'success': True})
    else:
        return redirect('logincheck')

    
#Order Management

def active_order(request):
    if request.session.get('signin') == True:
        order = Order.objects.all()
        orderproduct = OrderProduct.objects.filter(Q(status = 'Placed')|Q(status = 'Shipped')).order_by('-created_at')
        payment = Payment.objects.all()
        return render(request, 'admin/active_order.html', {'orders':order, 'orderproducts': orderproduct, 'payments': payment})
    else:
        return redirect('logincheck')


def ad_order_history(request):
    if request.session.get('signin') == True:
        order = Order.objects.all()
        orderproduct = OrderProduct.objects.filter(Q(status = 'Delivered')|Q(status = 'Returned')|Q(status = 'Cancelled')).order_by('-created_at')
        return render(request, 'admin/order_history.html', {'orders':order, 'orderproducts': orderproduct})
    else:
        return redirect('logincheck')

#Coupon Management

def admin_coupon(request):
    if request.session.get('signin') == True:
        form = CouponForm()
        today = date.today()
        if request.method == 'POST':
            form = CouponForm(request.POST)
            if form.is_valid():
                code = form.cleaned_data['code']
                form.save()
                coupon = Coupon.objects.get(code=code)
                try:
                    Coupon.objects.get(code__iexact=code,
                                        valid_from__lte = today,
                                        valid_to__gte = today,
                                        )
                    Coupon.objects.filter(id=coupon.id).update(status=True)
                except:
                    Coupon.objects.filter(id=coupon.id).update(status=False)
                return redirect('admin_coupon_list' )
            else:
                return redirect('admin_coupon')
        context = {'form': form}
        return render(request, "admin/new_coupon.html", context)
    else:
        return redirect('logincheck')


def admin_coupon_list(request):
    if request.session.get('signin') == True:
        coupon = Coupon.objects.all()
        today = date.today()
        for cpn in coupon:
            if cpn.valid_from <= today and cpn.valid_to >= today:
                Coupon.objects.filter(id=cpn.id).update(status=True)
                
            else:
                Coupon.objects.filter(id=cpn.id).update(status=False)
        context = {'coupon': coupon}
        return render(request, 'admin/coupon_list.html', context)
    else:
        return redirect('logincheck')


def coupon_edit(request, id):
    if request.session.get('signin') == True:
        today = date.today()
        qs = get_object_or_404(Coupon, id=id)
        form = CouponForm(instance=qs)
        if request.method == 'POST':
            form = CouponForm(request.POST, instance=qs)
            if form.is_valid():
                form.save()
                if qs.valid_from <= today and qs.valid_to >= today:
                    Coupon.objects.filter(id=qs.id).update(status=True)
                   
                else:
                    Coupon.objects.filter(id=qs.id).update(status=False)
                   
                return redirect('admin_coupon_list')
        context = {'form': form}
        return render(request, 'admin/admin_coupon_edit.html', context)
    else:
        return redirect('logincheck')


def coupon_delete(request):
    if request.session.get('signin') == True:
        coupon_id = request.POST['id']
        coupon_delete = Coupon.objects.get(id=coupon_id)
        coupon_delete.delete()
        return JsonResponse({'success': True})
    else:
        return redirect('logincheck')


#Report Management

def order_reports(request):
        if request.method == 'POST':
            product = Product.objects.all()
            date_from = request.POST['datefrom']
            date_to = datetime.datetime.strptime(request.POST['dateto'], "%Y-%m-%d")
            date_to = date_to + datetime.timedelta(days=1)
            date_to = datetime.datetime.strftime(date_to, "%Y-%m-%d")            
            order_search=Order.objects.filter(created_at__range=[date_from,date_to])
            return render(request, 'admin/admin_reports.html', {'reports': order_search})
        else:
            product = Product.objects.all()
            reports = OrderProduct.objects.all()
            coupon = Coupon.objects.all()
            context = {
                
                'coupon':coupon,
                'product':product,
                'reports':reports
            }
            return render(request, 'admin/admin_reports.html',context)



def order_export_csv(request):
    if request.session.get('signin') == True:
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename = Orders ' + \
            str(datetime.datetime.now()) + '.csv'

        writer = csv.writer(response)
        writer.writerow(['ORDER NUMBER', 'FULL NAME', 'PHONE',
                        'EMAIL', 'ORDER TOTAL', 'CREATED AT'])

        orders = Order.objects.filter(is_ordered=True).order_by('-created_at')

        for order in orders:
            writer.writerow([order.order_number, order.full_name(
            ), order.phone, order.email, order.order_total, order.created_at])

        return response
    else:
        return redirect('logincheck')


def order_export_excel(request):
    if request.session.get('signin') == True:
        response = HttpResponse(content_type='application/ms-excel')
        response['Content-Disposition'] = 'attachment; filename = Orders ' + \
            str(datetime.datetime.now()) + '.xls'

        wb = xlwt.Workbook(encoding='utf-8')
        ws = wb.add_sheet('Orders')
        row_num = 0
        font_style = xlwt.XFStyle()
        font_style.font.bold = True

        columns = ['ORDER NUMBER', 'FULL NAME', 'PHONE',
                'EMAIL', 'ORDER TOTAL', 'TAX', 'CREATED AT']

        for col_num in range(len(columns)):
            ws.write(row_num, col_num, columns[col_num], font_style)

        font_style = xlwt.XFStyle()

        rows = Order.objects.filter(is_ordered=True).order_by('-created_at').values_list(
            'order_number', 'first_name', 'phone', 'email', 'order_total', 'created_at')

        for row in rows:
            row_num += 1

            for col_num in range(len(row)):
                ws.write(row_num, col_num, str(row[col_num]), font_style)

        wb.save(response)

        return response
    else:
        return redirect('logincheck')


def order_export_pdf(request):
    if request.session.get('signin') == True:
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = 'inline; attachment; filename = Orders ' + \
            str(datetime.datetime.now()) + '.pdf'
        response['Content-Transfer-Encoding'] = 'binary'

        orders = Order.objects.filter(is_ordered=True).order_by('-created_at')

        html_string = render_to_string('admin/pdf_output.html', {
                                    'orders': orders, 'total': 0})
        html = HTML(string=html_string)

        result = html.write_pdf()

        with tempfile.NamedTemporaryFile(delete=True) as output:
            output.write(result)
            output.flush()
            output = open(output.name, 'rb')
            response.write(output.read())

        return response    
    else:
        return redirect('logincheck')
