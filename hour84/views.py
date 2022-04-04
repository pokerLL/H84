from django.shortcuts import render,redirect
from django.http import HttpResponse, JsonResponse
from django.conf import settings
import os

# Create your views here.


def index(request):
    return render(request, 'hour84/index.html')

def getProfilePicUrl(username):
    return os.path.join(settings.MEDIA_ROOT,username+'.jpg')


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
        _path =  getProfilePicUrl(_username)
        _dest = open(_path,'wb+')
        for chunk in _file.chunks():
            _dest.write(chunk)
        _dest.close()
        return JsonResponse({'path':_path})

def test(request):
    return render(request,'hour84/test.html',{})