from django.contrib.gis.db import models

class AccentPoint(models.Model):
    location = models.PointField(geography=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.location.x}, {self.location.y}"
