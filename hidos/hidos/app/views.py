"""
Definition of views.
"""

from django.shortcuts import render

version = '0.2.0'

def home(request):
    return render(request, 'app/homepage.html', {'title': 'Home', 'version': version})

