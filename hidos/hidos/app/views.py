"""
Definition of views.
"""

from django.shortcuts import render

def home(request):
    return render(request, 'app/homepage.html', {'title': 'Home'})