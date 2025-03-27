import requests
import os
from django.core.cache import cache
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions, throttling
from .models import WeatherRecord
from .serializers import WeatherRecordSerializer

class WeatherRateThrottle(throttling.UserRateThrottle):
    rate = '10/min'

class WeatherDetailView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    throttle_classes = [WeatherRateThrottle]

    def get(self, request):

        API_KEY = os.getenv('OPENWEATHER_API_KEY')
        # print(API_KEY)
        if not API_KEY:
            return Response({'error': 'API key not found.'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        
        city = request.query_params.get('city')
        if not city:
            return Response({'error': 'City is required.'}, status=status.HTTP_400_BAD_REQUEST)
        
        url_city = f"https://api.openweathermap.org/geo/1.0/direct?q={city}&limit=1&appid={API_KEY}"
        external_response = requests.get(url_city)
        if external_response.status_code != 200:
            return Response({'error': 'Error fetching weather data from external API.'},status=external_response.status_code)
        data = external_response.json()
        try:
            lon = data[0]['lon']
            lat = data[0]['lat']
        except (KeyError, IndexError):
            return Response({'error': 'Invalid location format received from weather API for the city.'},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        
        cache_key = f"weather_{lon}_{lat}"
        cached_data = cache.get(cache_key)
        if cached_data:
            print('Cache hit')
            return Response(cached_data)

        url = f'https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={API_KEY}'
        # url = f"https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&units=metric&appid={API_KEY}"
        external_response = requests.get(url)
        if external_response.status_code != 200:
            return Response({'error': 'Error fetching weather data from external API.'},
                            status=external_response.status_code)

        data = external_response.json()
        try:
            temperature = data['main']['temp']
            description = data['weather'][0]['description']
        except (KeyError, IndexError):
            return Response({'error': 'Invalid data format received from weather API.'},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        record = WeatherRecord.objects.create(
            user=request.user,
            longitude=lon,
            latitude=lat,
            temperature=temperature,
            description=description
        )
        serializer = WeatherRecordSerializer(record)
        result = serializer.data

        cache.set(cache_key, result, timeout=int(os.getenv('redis_cache_timeout_wtr_dtl', 60)))
        return Response(result, status=status.HTTP_200_OK)


from rest_framework.pagination import PageNumberPagination
class WeatherHistoryView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        records = WeatherRecord.objects.filter(user=request.user).order_by('-timestamp')
        
        paginator = PageNumberPagination()
        paginator.page_size = os.getenv('PAGINATOR_PAGE_SIZE',10)
        
        paginated_records = paginator.paginate_queryset(records, request)
        
        serializer = WeatherRecordSerializer(paginated_records, many=True)
        
        return paginator.get_paginated_response(serializer.data)