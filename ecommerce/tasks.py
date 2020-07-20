from __future__ import absolute_import, unicode_literals
from django.contrib.auth.models import User
from celery import shared_task
from django.core.mail import EmailMessage
from django.conf import settings
# from django.template.loader import render_to_string

@shared_task
def post_signup_welcome_mail(username=None):
    print("In post Signup welcome mail: Username={}".format(username))
    user = User.objects.filter(username=username).first()
    if user:
        print("Welcome user:{username}".format(username=user.username))
        # template = render_to_string('website/template/email-template.html', name=username)
        email = EmailMessage(
            'Welcome to ecommerce Karma',
            'We are very honored to welcome you at our Karma Website.',
            settings.EMAIL_HOST_USER,
            [user.email],
            )
        email.fail_silently = False
        email.send()
    else:
        print("User not found")

@shared_task
def order_mail(username=None, order=None):
    print("In post Signup welcome mail: Username={}".format(username))
    user = User.objects.filter(username=username).first()
    if user:
        print("Welcome user:{username}".format(username=user.username))
        # template = render_to_string('website/template/email-template.html', name=username)
        if order:
            for items in order:
                print(items)
            email = EmailMessage(
                'Order Info',
                'Your order is placed Successfully.',
                settings.EMAIL_HOST_USER,
                [user.email],
                )
            email.fail_silently = False
            email.send()
        else:
            email = EmailMessage(
                'Order Info',
                'Sorry, for the inconvenience caused, the item you have ordered is out of stock.',
                settings.EMAIL_HOST_USER,
                [user.email],
            )
            email.fail_silently = False
            email.send()
    else:
        print("User not found")