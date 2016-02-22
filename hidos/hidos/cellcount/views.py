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



