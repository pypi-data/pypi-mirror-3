

from django.shortcuts import render_to_response, get_object_or_404, redirect


def index(request):
    return redirect('/blog/')

