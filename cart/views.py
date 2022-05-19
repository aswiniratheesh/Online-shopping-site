from datetime import timezone
from django.utils import timezone

from django.shortcuts import render, redirect, get_object_or_404
from ecommerce_app.models import Product
from .models import Cart, CartItem, CouponCheck,Coupons as Coupon,Buynow,Wishlist
from django.core.exceptions import ObjectDoesNotExist
from accounts.models import Account
from admin_app.forms import CheckoutForm
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http.response import JsonResponse
from orders.models import DeliveryAddress
from datetime import date
# Create your views here.


def _cart_id(request):
    cart = request.session.session_key
    if not cart:
        cart = request.session.create()
    return cart


@login_required(login_url='user_login')
def add_cart(request, product_id):
    url = request.META.get('HTTP_REFERER')

    current_user = request.user
    product = Product.objects.get(id=product_id)
    if current_user.is_authenticated:
        try:
            cart = Cart.objects.get(cart_id=_cart_id(request))
        except Cart.DoesNotExist:
            cart = Cart.objects.create(
                cart_id=_cart_id(request)
            )
        cart.save()

        try:
            cart_item = CartItem.objects.get(product=product, user=current_user)
            if cart_item.quantity < product.stock:
                cart_item.quantity += 1
                cart_item.save()
            else:
                pass
               
         
        except CartItem.DoesNotExist:
            cart_item = CartItem.objects.create(
                product=product,
                quantity=1,
                user=current_user )
            cart_item.save()
    return redirect(url)

def add_item(request):
    product_id = request.POST['id']
    current_user = request.user
    product = Product.objects.get(id=product_id)

    if current_user.is_authenticated:
        try:
            cart = Cart.objects.get(cart_id=_cart_id(request))
        except Cart.DoesNotExist:
            cart = Cart.objects.create(
                cart_id=_cart_id(request)
            )
        cart.save()

        try:
            cart_item = CartItem.objects.get(product=product, user=current_user)
            if cart_item.quantity < product.stock:
                cart_item.quantity += 1
                cart_item.save()
            else:
                pass


        except CartItem.DoesNotExist:
            cart_item = CartItem.objects.create(
                product=product,
                quantity=1,
                user=current_user )
            cart_item.save()
    return JsonResponse({'success': True})

@login_required(login_url='user_login')
def cart(request, total=0, quantity=0, grandtotal=0, cart_items=None):
    
    try:
        if request.user.is_authenticated:
            cart_items = CartItem.objects.filter(user=request.user, active=True).order_by('-id')
        else:
            cart = Cart.objects.get(cart_id=_cart_id(request))
            cart_items = CartItem.objects.filter(cart=cart, active=True).order_by('-id')
        for cart_item in cart_items:
            total += (cart_item.product.price * cart_item.quantity)
            quantity += cart_item.quantity
        grandtotal +=total
    except ObjectDoesNotExist:
        pass

    context = {
        'total':total,
        'quantity':quantity,
        'cart_items': cart_items,
        'grandtotal': grandtotal,
    }
    return render(request, 'cart/cart.html',context)
    

@login_required(login_url='user_login')
def cart_remove(request):
    current_user = request.user
    product_id = request.POST['id']	

    product = get_object_or_404(Product, id=product_id)
    cart_item = CartItem.objects.get(product=product, user=current_user)
    if cart_item.quantity > 1:
        cart_item.quantity -= 1
        cart_item.save()
    else:
        cart_item.delete()
    return JsonResponse({'success': True})
   


@login_required(login_url='user_login')
def full_remove(request):
    current_user = request.user
    id = request.POST['id']
    product = get_object_or_404(Product, id=id)
    cart_item = CartItem.objects.get(product=product, user=current_user)
    cart_item.delete()
    return JsonResponse({'success': True})


@login_required(login_url='user_login')
def checkout(request, total=0, quantity=0, grandtotal=0, cart_items=None):
    today = date.today()
    coupon = Coupon.objects.all()
    for cpn in coupon:
        if cpn.valid_from <= today and cpn.valid_to >= today:
            Coupon.objects.filter(id=cpn.id).update(status=True)
            
        else:
            Coupon.objects.filter(id=cpn.id).update(status=False)
    try:
        if request.user.is_authenticated:
            cart_items = CartItem.objects.filter(user=request.user, active=True)
        else:
            cart = Cart.objects.get(cart_id=_cart_id(request))
            cart_items = CartItem.objects.filter(cart=cart, active=True)
        for cart_item in cart_items:
            total += (cart_item.product.price * cart_item.quantity)
            quantity += cart_item.quantity
        grandtotal +=total
    except ObjectDoesNotExist:
        pass

    adresses = DeliveryAddress.objects.all().filter(user = request.user)

    context = {
        'total':total,
        'quantity':quantity,
        'cart_items': cart_items,
        'grandtotal': grandtotal,
        'adresses':adresses,
    }

    return render(request, 'cart/checkout.html',context)


def checkCoupon(request, discount=0):
    if 'coupon_id' in request.session:
        del request.session['coupon_id']
        del request.session['grandtotal']
        del request.session['discount_price']

    flag = 0
    discount_price = 0
    today = date.today()
    coupon = request.POST['coupon']
    total = float(request.POST['total'])
    discount = 0
    if Coupon.objects.filter(code=coupon).exists():
        coup = Coupon.objects.get(code=coupon)

           
        if coup.status == True:
            flag = 1
            if not CouponCheck.objects.filter(user=request.user, coupon=coup):
                discount = total-(total*int(coup.discount)/100)
                discount_price = total*int(coup.discount)/100
                flag = 2
                request.session['grandtotal'] = discount
                request.session['discount_price'] = discount_price
                request.session['coupon_id'] = coup.id
    data = {
        
        'total': discount,
        'flag': flag,
        'discount_price': discount_price,

    }
    return JsonResponse(data)








@login_required(login_url='user_login')

def buy_now(request,id, total=0, quantity=0, buynow_items=None):
    Buynow.objects.all().delete()
    if 'coupon_id' in request.session:
        del request.session['coupon_id']
        del request.session['grandtotal']
        del request.session['discount_price']
    
    product = Product.objects.get(id=id)
    try:
        # get the cart using the cart id present in the session
        cart = Cart.objects.get(cart_id=_cart_id(request))
    except Cart.DoesNotExist:
        cart = Cart.objects.create(
            cart_id=_cart_id(request)
        )
    cart.save()

    try:
        buynow_item = Buynow.objects.get(product=product, user=request.user)
        if buynow_item.quantity > buynow_item.product.stock-1:
            return redirect('cart')
        else:
            buynow_item.quantity += 1
            buynow_item.save()


    except Buynow.DoesNotExist:
        buynow_item = Buynow.objects.create(
            product=product,
            quantity=1,
            user=request.user,
        )
        buynow_item.save()


    try:
        grand_total = 0
        if request.user.is_authenticated:
            buynow_items = Buynow.objects.filter(user=request.user, is_active=True)
        else:
            cart = Cart.objects.get(cart_id=_cart_id(request))
            buynow_items = Buynow.objects.filter(cart=cart, is_active=True)
        for buynow_item in buynow_items:
            total += (buynow_item.product.price * buynow_item.quantity)
            quantity += buynow_item.quantity
        grand_total = total

    except ObjectDoesNotExist:
        pass  # just ignore

    adresses = DeliveryAddress.objects.filter(user=request.user)

    context = {
        'total': total,
        'quantity': quantity,
        'buynow_items': buynow_items,
        'grand_total': grand_total,
        'adresses': adresses,
    }
    return render(request, 'buynow/buy_now_checkout.html', context)

@login_required(login_url='user_login')
def view_wishlist(request,id):
    wishlist = Wishlist.objects.filter(user=request.user)
    return render(request, 'wishlist.html',{'wishlist':wishlist})


def add_wishlist(request,id):
    url = request.META.get('HTTP_REFERER')
    product = Product.objects.get(id=id)
    if Wishlist.objects.filter(product=product, user=request.user).exists():
        pass
    else:
        Wishlist.objects.create(product=product, user=request.user)
    return redirect(url)

def del_wishlist(request,id):
    url = request.META.get('HTTP_REFERER')
    product = Product.objects.get(id=id)
    Wishlist.objects.get(product=product, user=request.user).delete()
    return redirect(url)

    

    
