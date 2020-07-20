from django.contrib import admin
from django.urls import path
from . import views
from rest_framework.authtoken import views as view

urlpatterns = [
    path('', views.products, name="index"),
    path('contact', views.contact, name="contact"),
    path('blog', views.blog, name="blog"),
    path('single-blog', views.singleBlog, name="single-blog"),
    path('register', views.registration, name="registration"),
    path('login', views.loginPage, name="login"),
    path('logout', views.logoutUser, name="logout"),
    path('tracking', views.tracking, name="tracking"),
    path('elements', views.elements, name="elements"),
    path('products', views.products, name="products"),
    path('single-product', views.singleProduct, name="single-product"),
    path('checkout', views.checkout, name="checkout"),
    path('cart', views.cart, name="cart"),
    path('confirmation', views.confirmation, name="confirmation"),
    path('api-token-auth', view.obtain_auth_token, name="api-token-auth"),
    path('update-item', views.updateItem, name="update-item"),
    path('process-order', views.processOrder, name="process-order"),
    path('view-profile', views.viewProfile, name="view-profile"),
]
