from django.shortcuts import render


# Create your views here.


def index(request):
    return render(request, 'hour84/index.html')


def login_or_register(request):
    pass
