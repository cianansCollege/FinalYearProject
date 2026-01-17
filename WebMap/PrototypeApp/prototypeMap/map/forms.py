from django import forms

class CoordinateForm(forms.Form):
    latitude = forms.FloatField()
    longitude = forms.FloatField()