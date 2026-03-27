from django.shortcuts import render
import os
from django.conf import settings
from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from .models import Prediction
from . import ml_module

# Frontend map page
def map_view(request):
    return render(request, "map.html")

# API: upload audio → prediction
@csrf_exempt
def predict_view(request):
    if request.method != "POST":
        return JsonResponse({"error": "POST required"}, status=400)

    if 'audio' not in request.FILES:
        return JsonResponse({"error": "No audio file provided"}, status=400)

    audio_file = request.FILES['audio']
    save_dir = os.path.join(settings.MEDIA_ROOT, "audio_storage")
    os.makedirs(save_dir, exist_ok=True)
    save_path = os.path.join(save_dir, audio_file.name)

    # Save the file
    with open(save_path, "wb+") as dest:
        for chunk in audio_file.chunks():
            dest.write(chunk)

    # Run ML prediction
    (lat, lng), confidence, label = ml_module.predict(save_path)

    # Save in DB
    pred = Prediction.objects.create(
        audio_file_path=save_path,
        latitude=lat,
        longitude=lng,
        confidence_score=confidence,
    )

    return JsonResponse({
        "id": pred.id,
        "lat": lat,
        "lng": lng,
        "confidence": confidence,
        "label": label,
    })

# API: list predictions for map
def predictions_view(request):
    preds = Prediction.objects.order_by("-timestamp")[:100]
    data = [
        {
            "id": p.id,
            "lat": p.latitude,
            "lng": p.longitude,
            "confidence": p.confidence_score,
            "timestamp": p.timestamp.isoformat()
        }
        for p in preds
    ]
    return JsonResponse(data, safe=False)

