from django.shortcuts import render,redirect,get_object_or_404
from django.contrib import messages
from django.core.exceptions import ValidationError
from django.http import JsonResponse
from ..schema.cities import City
from ..schema.countries import Country
from ..schema.states import State

def get_countries(request):
    countries = list(Country.objects.values("id", "name")) 
    return JsonResponse({"countries": countries}, status=200)

def get_states(request,country_id): 
    
    if not str(country_id).isdigit():
        return JsonResponse({"error": "Invalid state_id"}, status=400)
    
    states = list(State.objects.filter(country=country_id).values("id","statename"))
    return JsonResponse({"states":states}, status=200)

def get_cities(request,state_id):
    
    if not str(state_id).isdigit():
        return JsonResponse({"error": "Invalid state_id"}, status=400)
    
    cities = list(City.objects.filter(state=state_id).values("id","cityname"))
    return JsonResponse({"cities":cities}, status=200)