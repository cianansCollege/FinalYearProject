from django.db import models

class Prediction(models.Model):
    audio_file_path = models.CharField(max_length=255)
    timestamp = models.DateTimeField(auto_now_add=True)
    latitude = models.FloatField()
    longitude = models.FloatField()
    confidence_score = models.FloatField(null=True, blank=True)

    def __str__(self):
        return f"{self.id} @ ({self.latitude}, {self.longitude})"
