from django.shortcuts import render, redirect
from django.contrib.gis.geos import Point
from .models import AccentPoint
from .forms import CoordinateForm

def map_view(request):
    form = CoordinateForm()

    if request.method == "POST":
        form = CoordinateForm(request.POST)
        if form.is_valid():
            lat = form.cleaned_data["latitude"]
            lon = form.cleaned_data["longitude"]

            AccentPoint.objects.create(
                location=Point(lon, lat)
            )
            return redirect("map-page")

    last_points = AccentPoint.objects.order_by("-created_at")[:5]

    return render(request, "map/map.html", {
        "form": form,
        "points": last_points,
    })

