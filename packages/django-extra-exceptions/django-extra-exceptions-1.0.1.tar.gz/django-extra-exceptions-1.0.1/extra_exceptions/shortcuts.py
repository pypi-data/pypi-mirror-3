from django.http import Http404
from django.shortcuts import get_object_or_404, get_list_or_404
from .utils import bubble_message

def get_object_or(klass, exception, *args, **kwargs):
    try:
        return get_object_or_404(klass, *args, **kwargs)
    except Http404 as e:
        raise bubble_message(e,exception)
        
def get_list_or(klass, exception, *args, **kwargs):
    try:
        return get_list_or_404(klass, *args, **kwargs)
    except Http404 as e:
        raise bubble_message(e,exception)
