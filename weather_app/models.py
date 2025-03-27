from django.db import models
from django.conf import settings

class WeatherRecord(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    longitude = models.FloatField()
    latitude = models.FloatField()
    temperature = models.FloatField()
    description = models.CharField(max_length=255)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Weather for {self.user} at {self.timestamp}"
