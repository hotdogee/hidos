from django.shortcuts import render
from app.models import ImageAnalysis
from django.core.exceptions import ObjectDoesNotExist
# Create your views here.


def retrieve(request, task_id='1'):
    #return HttpResponse("retrieve = %s." % (task_id))
    try:
        record = ImageAnalysis.objects.get(task_id=task_id)
        return render(
            request,
            'app/result.html',
            {
                'title': 'CellQ - {0}'.format(record.user_filename),
                'year': datetime.now().year,
                'version': record.version,
                'user_filename': record.user_filename,
            }
        )
    except ObjectDoesNotExist:
        message = 'Result not found'
        return render(
            request,
            'app/error.html',
            {
                'title': 'CellQ Error',
                'year': datetime.now().year,
                'version': version,
                'message': message,
            }
        )
    except Exception as e:
        message = 'Result not found ({0})'.format(e.message)
        return render(
            request,
            'app/error.html',
            {
                'title': 'CellQ Error',
                'year': datetime.now().year,
                'version': version,
                'message': message,
            }
        )


def upload(request):
    """Renders the home page."""
    assert isinstance(request, HttpRequest)
    if request.method == 'GET':
        return render(
            request,
            'app/index.html',
            {
                'title':'Home',
                'year':datetime.now().year,
                'version': version,
            }
        )
    elif request.method == 'POST':
        # error detection
        if 'file' not in request.FILES:
            return HttpResponse('Invalid file')
        uploaded_file = request.FILES['file']
        # calculate file hash
        m = hashlib.md5()
        m.update(version)
        if request.user.is_authenticated():
            m.update(request.user.username)
        for chunk in uploaded_file.chunks():
            m.update(chunk)
        task_id = m.hexdigest()
        # check database for duplicate
        if not ImageAnalysis.objects.filter(task_id=task_id).exists():
            # setup file paths
            #task_id = uuid4().hex # TODO: Create from hash of input to check for duplicate inputs
            path_prefix = path.join(settings.MEDIA_ROOT, 'icsi', 'task', task_id, task_id)
            input_image_path = path_prefix + '_in.jpg'
            output_image_path = path_prefix
            output_json_path = path_prefix + '_out.json'

            if not path.exists(path.dirname(input_image_path)):
                makedirs(path.dirname(input_image_path))
            chmod(path.dirname(input_image_path), Perm.S_IRWXU | Perm.S_IRWXG | Perm.S_IRWXO) # ensure the standalone dequeuing process can open files in the directory
        
            # write query to file
            if 'file' in request.FILES:
                with open(input_image_path, 'wb') as input_image_f:
                    for chunk in uploaded_file.chunks():
                        input_image_f.write(chunk)
            chmod(input_image_path, Perm.S_IRWXU | Perm.S_IRWXG | Perm.S_IRWXO) # ensure the standalone dequeuing process can access the file

            # build command
            # set R_Script="C:\Program Files\R\R-3.2.2\bin\RScript.exe"
            # %R_Script% 1_6_obj_area_cal_cmd.R IMG_0159.JPG IMG_0159_out.JPG IMG_0159_out.csv
            script_path = path.join(settings.PROJECT_ROOT, 'icsi', 'bin', 'crop_auto.py')
            args_list = [[settings.PYTHON_SCRIPT, script_path,'--input', input_image_path,'--output',output_image_path]]
        
            # insert entry into database
            record = ImageAnalysis()
            record.task_id = task_id
            record.version = version
            record.user_filename = uploaded_file.name
            record.result_status = 'queued'
            if request.user.is_authenticated():
                record.user = request.user
            record.save()

            run_image_analysis_task.delay(task_id, args_list, path_prefix)

        # debug
        #run_image_analysis_task.delay(task_id, args_list, path_prefix).get()
        return HttpResponse(task_id)

