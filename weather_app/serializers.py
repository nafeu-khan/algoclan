from rest_framework import serializers
from .models import WeatherRecord

class WeatherRecordSerializer(serializers.ModelSerializer):
    class Meta:
        model = WeatherRecord
        fields = '__all__'
        read_only_fields = ('user', 'timestamp')
