from django.db import models
from django.contrib.auth.models import User

class Yield(models.Model):
    SOWING_METHODS = [
        ('ręczna', 'Ręczna'),
        ('maszynowa', 'Maszynowa'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='yields')
    image = models.ImageField(upload_to='yields_images/', null=True, blank=True, default='yields_images/default.svg')
    crop_name = models.CharField(max_length=100)
    area_ha = models.DecimalField(max_digits=6, decimal_places=2)
    yield_tons = models.DecimalField(max_digits=8, decimal_places=2)
    sowing_method = models.CharField(max_length=20, choices=SOWING_METHODS)
    sowing_date = models.DateField()
    harvest_date = models.DateField(null=True, blank=True)
    location = models.CharField(max_length=100)
    previous_crop = models.CharField(max_length=50)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.crop_name} - {self.area_ha} ha ({self.yield_tons})"

class Treatment(models.Model):
    TREATMENT_TYPES = [
        ('nawóz', 'Nawóz'),
        ('oprysk', 'Oprysk'),
        ('inne', 'Inne'),
    ]

    yield_record = models.ForeignKey(Yield, on_delete=models.CASCADE, related_name='treatments')
    treatment_type = models.CharField(max_length=20, choices=TREATMENT_TYPES)
    name = models.CharField(max_length=100)
    amount = models.CharField(max_length=10, blank=True)
    date = models.DateField()
    notes = models.TextField(blank=True)

    def __str__(self):
        return f"{self.get_treatment_type_display()} - {self.name} on {self.date}"

class MoistureMeasurement(models.Model):
    crop = models.ForeignKey(Yield, on_delete=models.CASCADE, related_name='moisture_measurements')
    date = models.DateField()
    moisture = models.DecimalField(max_digits=5, decimal_places=2)

    def __str__(self):
        return f"{self.date} - {self.moisture}% ({self.crop})"

class SoilPh(models.Model):
    crop = models.ForeignKey(Yield, on_delete=models.CASCADE, related_name='soil_phs')
    date = models.DateField()
    soil_ph = models.DecimalField(max_digits=3, decimal_places=1)

    def __str__(self):
        return f"{self.crop} - {self.soil_ph}"

class Temperature(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='temperatures')
    date = models.DateField()
    temperature = models.DecimalField(max_digits=4, decimal_places=1)

    def __str__(self):
        return f"{self.date} - {self.temperature}°C"

class Rainfall(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='rainfalls')
    date = models.DateField()
    rainfall = models.DecimalField(max_digits=5, decimal_places=1)

    def __str__(self):
        return f"{self.date} - {self.rainfall} mm"
