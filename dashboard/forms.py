from django import forms
from accounts.models import Yield, MoistureMeasurement, Treatment, SoilPh, Temperature, Rainfall



class YieldForm(forms.ModelForm):

    image = forms.ImageField(
        label='Zdjęcie uprawy',
        required=False,
        widget=forms.FileInput(attrs={'class': 'form-control'}),
    )

    crop_name = forms.CharField(
        label='Nazwa uprawy',
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )

    area_ha = forms.CharField(
        label='Obszar (ha)',
        widget=forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'})
    )

    yield_tons = forms.CharField(
        label='Ilość zebranych plonów (tony)',
        widget=forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'})
    )

    sowing_date = forms.DateField(
        label='Data siewu',
        widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
    )

    harvest_date = forms.DateField(
        label='Data zbioru',
        required=False,
        widget=forms.DateInput(format='%Y-%m-%d', attrs={'class': 'form-control', 'type': 'date'}),
    )

    location = forms.CharField(
        label='Lokalizacja',
        widget=forms.TextInput(attrs={'class': 'form-control'}),
    )

    previous_crop = forms.CharField(
        label='Poprzednia uprawa',
        widget=forms.TextInput(attrs={'class': 'form-control'}),
    )

    notes = forms.CharField(
        label='Opis',
        required=False,
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
    )

    class Meta:
        model = Yield
        fields = ['image', 'crop_name', 'area_ha', 'yield_tons', 'sowing_method', 'sowing_date', 'harvest_date', 'location', 'previous_crop', 'notes']
        widgets = {
            'sowing_method': forms.Select(attrs={'class': 'form-control'}),
        }

        labels = {
            'sowing_method': 'Metoda siewu',
        }

class MoistureMeasurementForm(forms.ModelForm):
    date = forms.DateField(
        label='Data pomiaru',
        required=True,
        widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'})
    )
    moisture = forms.DecimalField(
        label='Wilgotność [%]',
        required=True,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'})
    )

    class Meta:
        model = MoistureMeasurement
        fields = ['date', 'moisture']

class TreatmentForm(forms.ModelForm):
    date = forms.DateField(
        label='Data zabiegu',
        required=True,
        widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'})
    )

    class Meta:
        model = Treatment
        fields = ['treatment_type', 'name', 'amount', 'date', 'notes']
        widgets = {
            'treatment_type': forms.Select(attrs={'class': 'form-control'}),
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'amount': forms.TextInput(attrs={'class': 'form-control'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }
        labels = {
            'treatment_type': 'Typ zabiegu',
            'name': 'Nazwa środka',
            'amount': 'Ilość',
            'notes': 'Opis',
        }

class SoilPhForm(forms.ModelForm):
    date = forms.DateField(
        label='Data pomiaru',
        required=True,
        widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'})
    )

    soil_ph = forms.DecimalField(
        label='Ph gleby',
        required=True,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'step': '0.1'})
    )

    class Meta:
        model = SoilPh
        fields = ['date', 'soil_ph']

class TemperatureForm(forms.ModelForm):
    date = forms.DateField(
        label='Data pomiaru',
        required=True,
        widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'})
    )

    temperature = forms.DecimalField(
        label='Temperatura powietrza (℃)',
        required=True,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'step': '0.1'})
    )

    class Meta:
        model = Temperature
        fields = ['date', 'temperature']

class RainfallForm(forms.ModelForm):
    date = forms.DateField(
        label='Data pomiaru',
        required=True,
        widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'})
    )

    rainfall = forms.DecimalField(
        label='Opady (mm)',
        required=True,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'step': '0.1'})
    )

    class Meta:
        model = Rainfall
        fields = ['date', 'rainfall']

class ReportsForm(forms.Form):
    crop = forms.ModelChoiceField(
        queryset=Yield.objects.all(),
        label='Wybierz uprawę',
        widget=forms.Select(attrs={'class': 'form-control'}),
    )

    include_treatments = forms.BooleanField(label="Zabiegi", required=False)
    include_moisture = forms.BooleanField(label="Wilgotność gleby", required=False)
    include_soil_ph = forms.BooleanField(label="pH gleby", required=False)
    include_temperature = forms.BooleanField(label="Temperatura", required=False)
    include_rainfall = forms.BooleanField(label="Opady", required=False)

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        if user:
            self.fields['crop'].queryset = Yield.objects.filter(user=user)

