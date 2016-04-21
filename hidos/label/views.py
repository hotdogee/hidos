from django.shortcuts import render
from icsi.models import Ovum
from django.conf import settings

def home(request):

    ovum_all = Ovum.objects.all()
    ovums_list = []
    for o in ovum_all:
        ovum_dict = dict()
        ovum_dict['path'] = settings.MEDIA_URL + 'icsi/task/' + o.parent_imageanalysis_id + '/'  + o.ovum_id + '.jpg'
        ovum_dict['file_name'] = o.parent_imageanalysis.user_filename
        ovums_list.append(ovum_dict)


    return render(request,'label/label_home.html', {"ovums_list":ovums_list})
