from django.shortcuts import render, redirect
import requests
from datetime import datetime,  timedelta
from .models import City
from .forms import CityForm


def index(request):
    url = 'http://api.openweathermap.org/data/2.5/weather?q={}&appid=52724704c66e10e06ff1410aa146eda7'
    error_message = ""
    status = 0
    if request.method == 'POST':
        city_count = City.objects.all().count()
        print(city_count)
        if city_count < 6:
            form = CityForm(request.POST)
            if form.is_valid():
                new_city = form.cleaned_data['name']
                is_city_exist = City.objects.filter(name=new_city).count()
                r = requests.get(url.format(new_city)).json()
            if not is_city_exist and r['cod'] == 200:
                form.save()
                error_message = 'Successfully Added the city in the list!'
                status = 1
            elif is_city_exist:
                error_message = "The city is already in the List!"
            else:
                error_message = "There is not city in the world called " + new_city
        else:
            error_message = "You can not add more than 6 cities in that list. Please try after removing one of the cities below."

    form = CityForm()

    cities = City.objects.all()
    weather_list = []
    for city in cities:
        r = requests.get(url.format(city)).json()
        city_weather = {
            'city': city,
            'temperature': int(r['main']['temp']-273.15),
            'feel': int(r['main']['feels_like']-273.15),
            'description': r['weather'][0]['description'],
            'country': r['sys']['country'],
            'time': datetime.utcnow() + timedelta(seconds=r['timezone']),
            'icon': r['weather'][0]['icon'],

        }
        weather_list.append(city_weather)

    return render(request, 'index.html', {
        'weather_list': weather_list,
        'form': form,
        'error_message': error_message,
        'status': status
    })


def delete_city(request, city_name):
    City.objects.get(name=city_name).delete()
    return redirect('home')
