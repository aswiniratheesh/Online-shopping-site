from accounts.models import Account
from cart.views import checkout
from django.http import request
from django.http.response import HttpResponse, JsonResponse
from orders.models import DeliveryAddress, Order, OrderProduct,Payment
from django import forms
from django.shortcuts import redirect, render
from cart.models import Cart, CartItem,Buynow
from . forms import OrderForm, DeliveryAddressForm
import datetime
import json
from cart.models import Coupons as Coupon,CouponCheck
from ecommerce_app.models import Product
from accounts.models import Account

import xlwt
from django.template.loader import render_to_string
import tempfile
from weasyprint import HTML

# Create your views here.


def payment(request):
    body = json.loads(request.body)
    order = Order.objects.get(user = request.user, is_ordered = False, order_number = body['orderID'] )

    payment = Payment(
        user = request.user,
        payment_id = body['transID'],
        payment_method = body['payment_method'],
        amount_paid = order.order_total,
        status = body['status'],

    )
    payment.save()

    order.payment = payment
    order.is_ordered = True
    order.save()

    if 'coupon_id' in request.session:
        coupon_id = request.session['coupon_id']
        coupon = Coupon.objects.get(id=coupon_id)
        CouponCheck.objects.create(user=request.user, coupon= coupon)

        
    cart_items = CartItem.objects.filter(user=request.user)

    for item in cart_items:
        orderproduct = OrderProduct()
        orderproduct.order_id = order.id
        orderproduct.payment = payment
        orderproduct.user_id = request.user.id
        orderproduct.product_id = item.product_id
        orderproduct.quantity = item.quantity
        orderproduct.product_price = item.product.price
        orderproduct.ordered = True
        orderproduct.save()
        
        product = Product.objects.get(id=item.product_id)
        product.stock -= item.quantity
        product.save()

    CartItem.objects.filter(user=request.user).delete()
    
    data = {
        'order_number': order.order_number,
        'transID': payment.payment_id,
    }

    return JsonResponse(data)



def place_order(request,total=0,quantity=0):

    current_user=request.user 
    cart_items=CartItem.objects.filter(user=current_user)
    cart_count=cart_items.count()
    if cart_count <= 0:
        return redirect('home')
    pre_grand_total=0
    discount=0
    for cart_item in cart_items:
        total += (cart_item.product.price * cart_item.quantity)
        quantity += cart_item.quantity
    pre_grand_total=total

    if 'coupon_id' in request.session:
        discount = request.session['discount_price']
        grand_total = request.session['grandtotal']  

    else:
        discount = 0
        grand_total = pre_grand_total

    if request.method == 'POST':
        form=OrderForm(request.POST)
        if form.is_valid():
            data=Order()
            data.user=current_user
            data.first_name=form.cleaned_data['first_name']
            data.last_name=form.cleaned_data['last_name']
            data.phone=form.cleaned_data['phone']
            data.email=form.cleaned_data['email']
            data.address_line_1=form.cleaned_data['address_line_1']
            data.address_line_2=form.cleaned_data['address_line_2']
            data.country=form.cleaned_data['country']
            data.state=form.cleaned_data['state']
            data.city=form.cleaned_data['city']
            data.pincode=form.cleaned_data['pincode']
            data.order_total=grand_total
            data.ip=request.META.get('REMOTE_ADDR')
            data.save()
            #generate order number
            yr=int(datetime.date.today().strftime('%Y'))
            dt=int(datetime.date.today().strftime('%d'))
            mt=int(datetime.date.today().strftime('%m'))
            d=datetime.date(yr,mt,dt)
            current_date=d.strftime("%Y%m%d")
            order_number=current_date + str(data.id)
            data.order_number=order_number
            data.save()
           
            order=Order.objects.get(user=current_user, is_ordered=False, order_number=order_number)

            context={
                'order': order,
                'cart_items': cart_items,
                'total': total,
                'grand_total': grand_total,
                'discount':discount
                
            }
            return render(request,'orders/payments.html',context)
        else:
            return redirect('checkout')
    else:
        return redirect('checkout')

def order_complete(request):
    order_number = request.GET.get('order_number')
    transID = request.GET.get('payment_id')

    try:
        order = Order.objects.get(order_number=order_number, is_ordered=True)
        ordered_products = OrderProduct.objects.filter(order_id=order.id)
        subtotal = 0
        for i in ordered_products:
            total = i.product_price * i.quantity
            subtotal += total

        payment = Payment.objects.get(payment_id=transID)
        if 'coupon_id' in request.session:
            discount = request.session['discount_price']
            grand_total = request.session['grandtotal']  

        else:
            discount = 0
            grand_total = subtotal

        context = {
            'order': order,
            'ordered_products': ordered_products,
            'order_number': order.order_number,
            'transID': payment.payment_id,
            'payment': payment,
            'grand_total': grand_total,
            'discount':discount,
            'subtotal':subtotal,
            'total':total
        }

        return render(request, 'orders/order_complete.html', context)
    except (Payment.DoesNotExist, Order.DoesNotExist):
        return redirect('home')    


def order_history(request):
    
    order_item = OrderProduct.objects.filter(user = request.user).order_by('-created_at')

    return render(request, 'orders/order_history.html', {'order_item': order_item })
    
def status(request):
    id = request.POST['id']
    status = request.POST['status']
    OrderProduct.objects.filter(id=id).update(status=status)
    return JsonResponse({'success':True})


def order_cancel(request,orderPro_id):
    cancel_order = OrderProduct.objects.get(id=orderPro_id)
    Product.objects.filter(id=cancel_order.product.id).update(stock=cancel_order.product.stock + cancel_order.quantity)
    OrderProduct.objects.filter(id=orderPro_id).update(status="Cancelled")
    return redirect('order_history')


def order_return(request,orderPro_id):
    cancel_order = OrderProduct.objects.get(id=orderPro_id)
    Product.objects.filter(id=cancel_order.product.id).update(stock=cancel_order.product.stock + cancel_order.quantity)

    OrderProduct.objects.filter(id=orderPro_id).update(status="Returned")
    return redirect('order_history')


def add_address(request):

    url = request.META.get('HTTP_REFERER')

    if request.method == 'POST':
        address_form = DeliveryAddressForm(request.POST)
        if address_form.is_valid():
            address = address_form.save(commit=False)
            address.user = request.user
            address.save()
            print('saved')
            return redirect('checkout')
        else:
            print('ddd')
    else:
        address_form = DeliveryAddressForm()

    addresses = DeliveryAddress.objects.filter(user=request.user)

    context = {
        'address_form': address_form,
        'addresses': addresses,
    }

    return render(request, 'orders/addresses.html', context)


def buynow_place_order(request,total=0,quantity=0):

    current_user=request.user 
    buynow_items = Buynow.objects.filter(user=current_user)    
    buynow_count=buynow_items.count()
    if buynow_count <= 0:
        return redirect('home')
    pre_grand_total=0
    discount=0
    for buynow_item in buynow_items:
        total += (buynow_item.product.price * buynow_item.quantity)
        quantity += buynow_item.quantity
    pre_grand_total=total

    if 'coupon_id' in request.session:
        discount = request.session['discount_price']
        grand_total = request.session['grandtotal']  

    else:
        discount = 0
        grand_total = pre_grand_total

    if request.method == 'POST':
        form=OrderForm(request.POST)
        if form.is_valid():
            data=Order()
            data.user=current_user
            data.first_name=form.cleaned_data['first_name']
            data.last_name=form.cleaned_data['last_name']
            data.phone=form.cleaned_data['phone']
            data.email=form.cleaned_data['email']
            data.address_line_1=form.cleaned_data['address_line_1']
            data.address_line_2=form.cleaned_data['address_line_2']
            data.country=form.cleaned_data['country']
            data.state=form.cleaned_data['state']
            data.city=form.cleaned_data['city']
            data.pincode=form.cleaned_data['pincode']
            data.order_total=grand_total
            data.ip=request.META.get('REMOTE_ADDR')
            data.save()
            #generate order number
            yr=int(datetime.date.today().strftime('%Y'))
            dt=int(datetime.date.today().strftime('%d'))
            mt=int(datetime.date.today().strftime('%m'))
            d=datetime.date(yr,mt,dt)
            current_date=d.strftime("%Y%m%d")
            order_number=current_date + str(data.id)
            data.order_number=order_number
            data.save()
           
            order=Order.objects.get(user=current_user, is_ordered=False, order_number=order_number)

            context={
                'order': order,
                'buynow_items': buynow_items,
                'total': total,
                'grand_total': grand_total,
                'discount':discount
                
            }
            return render(request,'buynow/buynow_payments.html',context)
        else:
            return redirect('buy_now')
    else:
        return redirect('buy_now')

def buynow_payment(request):
    body = json.loads(request.body)
    order = Order.objects.get(user = request.user, is_ordered = False, order_number = body['orderID'] )

    payment = Payment(
        user = request.user,
        payment_id = body['transID'],
        payment_method = body['payment_method'],
        amount_paid = order.order_total,
        status = body['status'],

    )
    payment.save()
    order.payment = payment
    order.is_ordered = True
    order.save()

    if 'coupon_id' in request.session:
        coupon_id = request.session['coupon_id']
        coupon = Coupon.objects.get(id=coupon_id)
        CouponCheck.objects.create(user=request.user, coupon= coupon)

        
    buynow_items = Buynow.objects.filter(user=request.user)

    for item in buynow_items:
        orderproduct = OrderProduct()
        orderproduct.order_id = order.id
        orderproduct.payment = payment
        orderproduct.user_id = request.user.id
        orderproduct.product_id = item.product_id
        orderproduct.quantity = item.quantity
        orderproduct.product_price = item.product.price
        orderproduct.ordered = True
        orderproduct.save()
        
        product = Product.objects.get(id=item.product_id)
        product.stock -= item.quantity
        product.save()

    Buynow.objects.filter(user=request.user).delete()
    
    data = {
        'order_number': order.order_number,
        'transID': payment.payment_id,
    }

    return JsonResponse(data)


