from django.contrib import admin
from .models import Yield, Treatment, MoistureMeasurement, SoilPh, Temperature, Rainfall

admin.site.register(Yield)
admin.site.register(Treatment)
admin.site.register(MoistureMeasurement)
admin.site.register(SoilPh)
admin.site.register(Temperature)
admin.site.register(Rainfall)
