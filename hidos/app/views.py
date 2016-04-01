"""
Definition of views.
"""

from django.shortcuts import render, redirect

version = '0.2.0'

def home(request):
    return redirect('/icsi')
    # return render(request, 'app/homepage.html', {'title': 'Home', 'version': version})

