from django.shortcuts import render
from django.http import HttpResponse
import exchange_rates


def index(request):
    return HttpResponse(exchange_rates)
