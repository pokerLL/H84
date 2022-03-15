from django.shortcuts import render,redirect
from django.http import HttpResponse, JsonResponse
from django.conf import settings
import os

# Create your views here.


def index(request):
    return render(request, 'hour84/index.html')


def upload(request):
    if request.method == 'POST':
        _file = request.FILES.get('pic',None)
        if not _file:
            return HttpResponse('no files for upload!')
        # print(_file)
        try:
            os.makedirs(settings.MEDIA_ROOT)
        except:
            pass
        _username = request.POST.get('username')
        _path =  os.path.join(settings.MEDIA_ROOT,_username+'.jpg')
        _dest = open(_path,'wb+')
        for chunk in _file.chunks():
            _dest.write(chunk)
            print(_dest,'...')
        _dest.close()
        return JsonResponse({'path':_path})