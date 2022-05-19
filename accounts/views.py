from django.db.models import query
from django.shortcuts import render,redirect
from . models import Account
from django.contrib import messages
from django.contrib.auth.models import User, auth
from twilio.rest import Client
from twilio.base.exceptions import TwilioRestException
from cart.views import _cart_id
from cart.models import CartItem, Cart
import requests
from django.contrib.auth.decorators import login_required,user_passes_test
from django.views.decorators.cache import never_cache
from decouple import config



 # admin login  
def logincheck(request):
    if request.session.get('signin') == True:
        return redirect('admin_home')
    else:
        if request.method == 'POST':
            email = request.POST['email']
            password = request.POST['password']

            user = auth.authenticate(email=email,password=password)
            if user is not None:
                if user.is_superuser == True:
                    auth.login(request, user)
                    request.session['signin'] = True
                    return redirect('admin_home')
                else:
                    messages.info(request, 'invalid credentials')
                    return redirect('logincheck')
            else:
                messages.info(request, 'invalid credentials')
                return redirect('logincheck')
        else:
            return render(request,'admin/admin_login.html')


# admin logout
def admin_logout(request):
    if request.session.get('signin') == True:
        del request.session['signin']
        return redirect('logincheck')
    else:
        return redirect('logincheck')



# user signup
def user_reg(request):
    if request.session.get('login') == True:
        return redirect('/')
    else:
        if request.method == 'POST':
            first_name = request.POST['first_name']
            last_name = request.POST['last_name']
            username = request.POST['username']
            password1 = request.POST['password1']
            password2 = request.POST['password2']
            email = request.POST['email']
            phone_no = request.POST['phone_no']

            request.session['email'] = email
            request.session['phone_no'] = phone_no
            request.session['password1'] = password1
            request.session['username'] = username
            request.session['first_name'] = first_name
            request.session['last_name'] = last_name

            if password1 == password2:
                if Account.objects.filter(username=username).exists():
                    messages.error(request, 'Username already taken')
                    return redirect('signup')
                elif Account.objects.filter(email=email).exists():
                    messages.error(request,'Email already taken') 
                    return redirect('signup')
                elif Account.objects.filter(phone_no=phone_no).exists():
                    messages.error(request,'Phone Number already taken') 
                    return redirect('signup')
                else:
                    try:


                        account_sid = config('account_sid')
                        auth_token = config('auth_token')

                        client = Client(account_sid, auth_token)

                        verification = client.verify \
                            .services('VA8ba181d3b8ba0f7750f9b2297cc921a1') \
                            .verifications \
                            .create(to='+91'+phone_no, channel='sms')

                        print(verification.status)
                        return redirect('reg_otp')
                    except:
                        messages.info(request,'Invalid phone number') 
                        return redirect('signup')
            else:
                messages.info(request,'Password not matching') 
                return redirect('signup')
        else:
            return render(request, 'user/user_signup.html')







# registration OTP

def reg_otp(request):
    if request.method == 'POST':
        otp = request.POST['otp']

        email = request.session['email']
        phone_no = request.session['phone_no']
        password = request.session['password1']
        username =request.session['username'] 
        phone_no = request.session['phone_no']
        first_name = request.session['first_name']
        last_name = request.session['last_name']


        account_sid = config('account_sid')
        auth_token = config('auth_token')

        client = Client(account_sid, auth_token)

        verification_check = client.verify \
            .services('VA8ba181d3b8ba0f7750f9b2297cc921a1') \
            .verification_checks \
            .create(to='+91'+phone_no, code=otp)

        print(verification_check.status)

        if verification_check.status == 'approved':
            user = Account.objects.create_user(email=email,password=password,username=username,phone_no=phone_no,first_name=first_name,last_name=last_name)
            user.save()
            auth.login(request, user)
            return redirect('home')

        else:
            messages.error(request, 'OTP is not matching')
            del request.session['phone_no'] 
            del request.session['email'] 
            del request.session['password1']
            del request.session['username'] 
            del request.session['first_name'] 
            del request.session['last_name']

            return redirect('reg_otp')
    else:
        return render(request, 'user/reg_otp.html')



# user login

def user_login(request):
    if request.session.get('login') == True:
        return redirect('/')
    else:
        if request.method == 'POST':
            email = request.POST['email']
            password = request.POST['password']
            print(password)

            user = auth.authenticate(email=email,password=password)

            if user is not None  and  user.is_superuser == False :
                try:
                    cart = Cart.objects.get(cart_id=_cart_id(request))
                    is_cart_item_exists = CartItem.objects.filter(cart=cart).exists()
                    if is_cart_item_exists:
                        cart_item = CartItem.objects.get(cart=cart)
                        print(cart_item)
                        for item in cart_item:
                            item.user = user
                            item.save()
                            
                except:
                    pass
                auth.login(request, user)
                request.session['login'] = True
                url = request.META.get('HTTP_REFERER')
                try:
                    query = requests.utils.urlparse(url).query
                    params = dict(x.split('=')for x in query.split('&'))
                    if 'next' in params:
                        nextPage = params['next']
                        return redirect(nextPage)
                except:
                    return redirect('allproduct')
            else:
                messages.info(request, 'invalid credentials')
                return redirect('user_login')

        return render(request,'user/user_login.html')

# user logout
def user_logout(request):
    auth.logout(request)        
    return redirect('/')



# user - otp to phone

def phone_login(request):
    if request.session.get('login') == True:
        return redirect('/')
    else:
        if request.method == 'POST':
            phone_no = request.POST['phone_no']
        
            if Account.objects.filter(phone_no=phone_no):

                request.session['phone_no'] = phone_no


                account_sid = config('account_sid')
                auth_token = config('auth_token')


                client = Client(account_sid, auth_token)

                verification = client.verify \
                    .services('VA8ba181d3b8ba0f7750f9b2297cc921a1') \
                    .verifications \
                    .create(to='+91'+phone_no, channel='sms')

                print(verification.status)
                return redirect('login_otp')

            else:
                messages.info(request, 'Phone Number is not Registered')
                return redirect('phone_login')

        return render(request, 'user/phone_login.html')

    
# user otp login
def login_otp(request):
    if request.method == 'POST':
        otp = request.POST['otp']

        phone_no = request.session['phone_no']


        
        account_sid = config('account_sid')
        auth_token = config('auth_token')


        client = Client(account_sid, auth_token)

        verification_check = client.verify \
            .services('VA8ba181d3b8ba0f7750f9b2297cc921a1') \
            .verification_checks \
            .create(to='+91'+phone_no, code=otp)

        print(verification_check.status)

        if verification_check.status == 'approved':

            user = Account.objects.get(phone_no=phone_no)

            if user is not None:
                auth.login(request, user)
                request.session['login'] = True
                del request.session['phone_no']
                return redirect('/')
            else:
                return redirect('login_otp')

        else:
            messages.info(request, 'OTP is not matching')
            return redirect('login_otp')
    else:
        return render(request, 'user/login_otp.html')




def forgot_password(request):
    if request.session.get('login') == True:
        return redirect('/')
    else:
        if request.method == 'POST':
            phone_no = request.POST['phone_no']
        
            if Account.objects.filter(phone_no=phone_no):

                request.session['phone_no'] = phone_no


                account_sid = config('account_sid')
                auth_token = config('auth_token')

                client = Client(account_sid, auth_token)

                verification = client.verify \
                    .services('VA8ba181d3b8ba0f7750f9b2297cc921a1') \
                    .verifications \
                    .create(to='+91'+phone_no, channel='sms')

                print(verification.status)
                return redirect('forgot_otp')

            else:
                messages.info(request, 'Phone Number is not Registered')
                return redirect('phone_login')


        return render(request, 'user/forgot_password.html')

def forgot_otp(request):
    if request.method == 'POST':
        otp = request.POST['otp']

        phone_no = request.session['phone_no']



        account_sid = config('account_sid')
        auth_token = config('auth_token')
        
        client = Client(account_sid, auth_token)

        verification_check = client.verify \
            .services('VA8ba181d3b8ba0f7750f9b2297cc921a1') \
            .verification_checks \
            .create(to='+91'+phone_no, code=otp)

        print(verification_check.status)

        if verification_check.status == 'approved':

            user = Account.objects.get(phone_no=phone_no)

            if user is not None:
                return redirect('reset_password')
            else:
                return redirect('login_otp')

        else:
            messages.info(request, 'OTP is not matching')
            return redirect('login_otp')

    return render(request, 'user/forgot_otp.html')



def reset_password(request):
    if request.method == 'POST':
        password1 = request.POST['password1']
        password2 = request.POST['password2']
        if password1 == password2:
            phone_no = request.session['phone_no']
            user = Account.objects.get(phone_no=phone_no)
            user.set_password(password1)
            user.save()
            return redirect('user_login')
        else:
            messages.error(request, 'password not matching')
    else:
        return render(request, 'user/reset_password.html')
