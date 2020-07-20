from django.contrib.auth.forms import UserChangeForm
from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.contrib import messages
from django.core.mail import send_mail
from django.contrib.auth import authenticate, login, logout
from django.views.decorators.csrf import csrf_exempt
from rest_framework.authtoken.models import Token
from django.contrib.auth.decorators import login_required

from ecommerce.tasks import post_signup_welcome_mail, order_mail
from .forms import CreateUserForm, EditProfileForm
from .models import *
from .utils import cookieCart, cartData, guestOrder

import json
import datetime

# @login_required(login_url='login')
def index(request):
    return render(request, 'index.html', {})

def contact(request):
    if request.method == 'POST':
        name = request.POST['name']
        email = request.POST['email']
        subject = request.POST['subject']
        message = request.POST['message']

        # send an email
        send_mail(subject, message, email, ['shraddhagami03@gmail.com'])
        return render(request, 'contact.html', {'name': name})
    else:
        return render(request, 'contact.html', {})

# @login_required(login_url='login')
def products(request):
    data = cartData(request)
    cartItems = data['cartItems']

    products = Product.objects.all()
    context = {
        'products': products,
        'cartItems': cartItems
    }
    return render(request, 'products.html', context)



# @login_required(login_url='login')
def singleProduct(request):
    return render(request, 'single-product.html', {})

# @login_required(login_url='login')
def checkout(request):
    data = cookieCart(request)
    cartItems = data['cartItems']
    order = data['order']
    items = data['items']

    context = {
        'items': items,
        'order': order,
        'cartItems': cartItems
    }
    return render(request, 'checkout.html', context)

# @login_required(login_url='login')
def cart(request):
    data = cartData(request)
    cartItems = data['cartItems']
    order = data['order']
    items = data['items']

    context = {
        'items': items,
        'order': order,
        'cartItems': cartItems
    }
    return render(request, 'cart.html', context)

# @login_required(login_url='login')
def confirmation(request):
    return render(request, 'confirmation.html', {})

def blog(request):
    return render(request, 'blog.html', {})

def singleBlog(request):
    return render(request, 'single-blog.html', {})

def registration(request):
    if request.user.is_authenticated:
        return redirect('index')
    else:
        form = CreateUserForm()
        if request.method == 'POST':
            form = CreateUserForm(request.POST)
            if form.is_valid():
                form.save()
                user_name = form.cleaned_data.get('username')
                email = form.cleaned_data.get('email')
                user = User.objects.get(email=email)
                customer, created = Customer.objects.get_or_create(user=user)
                customer.email = email
                customer.save()

                #Send the user a welcome mail
                post_signup_welcome_mail.delay(user_name)

                messages.success(request, user_name+', Your account created Successfully')
                return redirect('login')
        data = cookieCart(request)
        cartItems = data['cartItems']
        context = {'form': form,
                   'cartItems': cartItems}
        return render(request, 'registration.html', context)

def loginPage(request):
    if request.user.is_authenticated:
        return redirect('index')
    else:
        if request.method == 'POST':
            username = request.POST.get('username')
            password = request.POST.get('password')

            user = authenticate(request, username=username, password=password)

            # token = Token.objects.create(user=user)

            # print(token.key)

            if user is not None:
                login(request, user)
                return redirect('index')
            else:
                messages.info(request, 'Username or Password is incorrect')

        data = cookieCart(request)
        cartItems = data['cartItems']
        context = {
            'cartItems': cartItems
        }
        return render(request, 'login.html', context)

# @login_required(login_url='login')
def logoutUser(request):
    logout(request)
    return render(request, 'login.html', {})

def viewProfile(request):
    customer = request.user.customer
    data = cartData(request)
    cartItems = data['cartItems']
    if request.method == "POST":
        form = EditProfileForm(request.POST, instance=customer)
        if form.is_valid():
            customer = form.save(commit=False)
            customer.user = request.user
            customer.save()
            return redirect('view-profile')
        else:

            context = {'form': form, 'cartItems': cartItems}
            return render(request, 'view-profile.html', context)
    else:
        context = {'customer': customer, 'cartItems': cartItems}
        return render(request, 'view-profile.html', context)


# def updateProfile(request):
#     if
#         form = UserChangeForm('request.POST', instance=request.user)
#
#         if form.is_valid():
#             form.save()
#             return redirect('index')
#     else:
#         data = cookieCart(request)
#         cartItems = data['cartItems']
#         context = {'cartItems': cartItems}
#         return render(request, 'view-profile.html', context)
#     else:
#         form = UserChangeForm('request.POST', instance=request.user)
#         data = cookieCart(request)
#         cartItems = data['cartItems']
#         context = {'form': form, 'cartItems': cartItems}
#         return render(request, 'view-profile.html', context)

# @login_required(login_url='login')
def tracking(request):
    return render(request, 'tracking.html', {})

# @login_required(login_url='login')
def elements(request):
    return render(request, 'elements.html', {})

def updateItem(request):
    data = json.loads(request.body)
    productId = data['productId']
    action = data['action']
    print('Action:', action)
    print('ProductId', productId)

    customer = request.user.customer
    product = Product.objects.get(id=productId)
    order, created = Order.objects.get_or_create(customer=customer, complete=False)

    orderItem, created = OrderItem.objects.get_or_create(order=order, product=product)

    if action == 'add':
        orderItem.quantity = orderItem.quantity + 1
    elif action == 'remove':
        orderItem.quantity = orderItem.quantity - 1

    orderItem.save()

    if orderItem.quantity <= 0:
        orderItem.delete()

    return JsonResponse('Item was added', safe=False)

@csrf_exempt
def processOrder(request):
    transaction_id = datetime.datetime.now().timestamp()
    data = json.loads(request.body)

    if request.user.is_authenticated:
        customer = request.user.customer
        order, created = Order.objects.get_or_create(customer=customer, complete=False)
    else:
        customer, order = guestOrder(request, data)

    total = float(data['form']['total'])
    order.transaction_id = transaction_id

    if total == order.get_cart_total:
        order_mail(username=request.user.username, order=order)
        order.complete = True
        # order_mail(customer, order)
    order.save()

    ShippingAddress.objects.create(
        customer=customer,
        order=order,
        address=data['shipping']['address'],
        city=data['shipping']['city'],
        state=data['shipping']['state'],
        zipcode=data['shipping']['zipcode'],
    )

    return JsonResponse('Payment Complete!', safe=False)

