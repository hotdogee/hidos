import os
from subprocess import call, Popen, PIPE
from django.http import HttpResponse, HttpResponseForbidden, HttpResponseRedirect
from django import template
from django.conf import settings
from django.shortcuts import render_to_response, RequestContext, render

def home(request):
    return render(request, 'tfMRI/home.html', locals())

def write_fsf(request):
    #with open('templates/write_fsf.html', 'r') as reader:
    #	t = template.Template(reader.read())
    #return HttpResponse(t)
    return render(request, 'tfMRI/write_fsf.html', locals())

def new_job(request):
    if request.method == 'POST':
        text = request.POST.get('show', '')
        text = text.replace('/path/to/output', os.path.join(settings.PROJECT_ROOT, 'media/tfMRI/outputs', '210_6'))
        text = text.replace('set fmri(npts) 24', 'set fmri(npts) 246')
        text = text.replace('set fmri(tr) 3.0', 'set fmri(tr) 2.000000 ')
        text = text.replace('C:\\fakepath\\', os.path.join(settings.PROJECT_ROOT, 'media/tfMRI/inputs/'))
        text = text.replace('.nii.gz', '')
        
        for item in text.split('\n'):
            if 'outputdir' in item:
                output_old = item
                break
        
        with open('media/tfMRI/inputs/design.fsf', 'w') as fsf_writer:
            fsf_writer.write(text)
        call(['dos2unix', 'media/tfMRI/inputs/design.fsf'])
        p = Popen(['feat', 'media/tfMRI/inputs/design.fsf'], stdout=PIPE, stderr=PIPE)
        stdout = p.stdout.readline().rstrip()
        outdir = stdout[stdout.find('outputs/'):-16]
        request.session['outdir'] = outdir
        
        pid = p.pid
        request.session['p'] = p
        request.session['text'] = text
        return render(request, 'tfMRI/running.html', locals())
    else:
        if 'p' in request.session:
            p = request.session['p']
            pid = p.pid
            if p.poll() is None:
                text = request.session['text']
                return render(request, 'tfMRI/running.html', locals())
            else:
                del request.session['p']
                del request.session['text']
                for html_file in ['report.html', 'report_reg.html', 'report_prestats.html', 'report_stats.html']:
                    with open (os.path.join(settings.PROJECT_ROOT, 'media/tfMRI', request.session['outdir'], html_file), 'r') as reader:
                        html = reader.read()
                    if html_file == 'report.html':
                        html = html.replace('<A HREF=report_poststats.html target=_top>Post-stats</A> &nbsp;-&nbsp;', '')
                        html = html.replace('<A HREF=report_log.html target=_top>Log</A>', '')
                        html = thml.replace('<A HREF=report_stats.html target=_top>Stats</A> &nbsp;-&nbsp;',
                                            '<A HREF=report_stats.html target=_top>Stats</A>')
                    html = replace_html(html, request.session['outdir'])
                    with open (os.path.join(settings.PROJECT_ROOT, 'tfMRI', 'templates', 'tfMRI', html_file), 'w') as writer:
                        writer.write(html)
                del request.session['outdir']
                return HttpResponseRedirect("/tfMRI/results/")
        else:
            return HttpResponseForbidden()
        
def replace_html(html, outdir):
    tmp = html
    tmp = '{% load static %}\n' + tmp
    tmp = '{% load staticfiles %}\n' + tmp
    tmp = tmp.replace('<TITLE>FSL</TITLE>', '<TITLE>Report</TITLE>')
    for lines in tmp.split('\n'):
        if '<tr><td valign=center height=25 align=center>' in lines:
            tmp = tmp.replace(lines, '')
    tmp = tmp.replace('HREF=report_reg.html', 'HREF="{% url \'freg\' %}"')
    tmp = tmp.replace('HREF=report_prestats.html', 'HREF="{% url \'fprestats\' %}"')
    tmp = tmp.replace('HREF=report_stats.html', 'HREF="{% url \'fstats\' %}"')
#    tmp = tmp.replace('HREF=report_poststats.html', 'HREF="{% url \'fpoststats\' %}"')
#    tmp = tmp.replace('HREF=report_log.html', 'HREF="{% url \'flog\' %}"')
    tmp = tmp.replace('href=.files/fsl.css', 'href="{% static \'tfMRI/css/fsl.css\' %}"')
    tmp = tmp.replace('<OBJECT data=report.html></OBJECT>', '<OBJECT data="{% url \'fresults\' %}"></OBJECT>')
    tmp = tmp.replace('SRC=reg', 'SRC="/media/tfMRI/'+outdir+'/reg')
    tmp = tmp.replace('SRC=mc', 'SRC="/media/tfMRI/'+outdir+'/mc')
    tmp = tmp.replace('SRC=design', 'SRC="/media/tfMRI/'+outdir+'/design')
    tmp = tmp.replace('.png', '.png"')
    return tmp

def show_result(request):
    return render(request, 'tfMRI/report.html', locals())

def show_reg(request):
    return render(request, 'tfMRI/report_reg.html', locals())

def show_prestats(request):
    return render(request, 'tfMRI/report_prestats.html', locals())

def show_stats(request):
    return render(request, 'tfMRI/report_stats.html', locals())

def show_poststats(request):
    return render(request, 'tfMRI/report_poststats.html', locals())

def show_log(request):
    return render(request, 'tfMRI/report_log.html', locals())
