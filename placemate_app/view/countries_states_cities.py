from django.shortcuts import render,redirect,get_object_or_404
from django.contrib import messages
from django.core.exceptions import ValidationError
from ..schema.cities import City
from ..schema.countries import Country
from ..schema.states import State
from ..utils.helper_utils import ResponseModel

def get_countries(request):
    countries = list(Country.objects.values("id", "name")) 
    return ResponseModel(countries,"Countries Fetch Successfully",200)

def get_states(request,country_id): 
    
    if not str(country_id).isdigit():
        return ResponseModel({},"Invalid country id",400)
    
    states = list(State.objects.filter(country=country_id).values("id","statename"))
    return ResponseModel(states,"States Fetch Successfully",200)

def get_cities(request,state_id):
    
    if not str(state_id).isdigit():
        return ResponseModel({},"Invalid state id",400)
    
    cities = list(City.objects.filter(state=state_id).values("id","cityname"))
    return ResponseModel(cities,"Cities Fetch Successfully",200)

def get_city_with_name(request):
    search = request.GET.get('search', '').strip()

    if not search:
        return ResponseModel({}, "No search query provided", 400)

    cities = list(
        City.objects.filter(cityname__istartswith=search).values("id", "cityname")
    )
    return ResponseModel(cities, f"Countries starting with '{search}' fetched successfully", 200)