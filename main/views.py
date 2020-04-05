from django.shortcuts import render

# Create your views here.
from django.http import HttpResponse,JsonResponse
from django.views.decorators.http import require_http_methods
from urllib.parse import unquote

# Import SQLINQ.py
import main.custom as s


# loading template use loader

from django.template import loader  

@require_http_methods(["GET"])
def Hello(Request):
    return HttpResponse("<h1>This is get</h1") 

# Rendering HTML File

@require_http_methods(["GET"])
def MainApp(Request):
    template = loader.get_template('main.html') # getting our template 
    return HttpResponse(template.render())

# @require_http_methods(["POST"])
def Show(Request):
    if Request.method == 'GET':
        query = Request.GET.get('query')
        query = unquote(query)
        # print("The value:" + str(query))
        result = {
            'value' : s.Convert(query)
        }
        return JsonResponse(result)
    