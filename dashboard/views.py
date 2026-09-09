import csv

from django.db.models import Sum, Avg
from django.templatetags.static import static
from weasyprint import HTML
import requests

from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from accounts.models import Yield, MoistureMeasurement, Treatment, SoilPh, Temperature, Rainfall
from django.template.loader import render_to_string
from django.utils.timezone import now

from .forms import YieldForm, MoistureMeasurementForm, TreatmentForm, SoilPhForm, TemperatureForm, RainfallForm, ReportsForm
import pandas as pd
import plotly.express as px

@login_required(login_url='login')
def dashboard(request):
    # Wyciąganie danych z bazy, sortowanie po dacie siewu
    yields = Yield.objects.filter(user=request.user).order_by('sowing_date')
    return render(request, 'dashboard.html',  {'yields': yields})

@login_required(login_url='login')
def stats(request):

    # Wyciąganie danych z bazy i obliczanie wartości średnich
    crops = Yield.objects.filter(user=request.user)
    total_area = round(crops.aggregate(total_area=Sum('area_ha'))['total_area'], 2) if crops.aggregate(total_area=Sum('area_ha'))['total_area'] is not None else 0
    total_yields = round(crops.aggregate(total_yields=Sum('yield_tons'))['total_yields'], 2) if crops.aggregate(total_yields=Sum('yield_tons'))['total_yields'] is not None else 0

    temperature = Temperature.objects.filter(user=request.user)
    avg_temperature = round(temperature.aggregate(Avg('temperature'))['temperature__avg'], 2) if temperature.aggregate(Avg('temperature'))['temperature__avg'] is not None else '-'

    rainfall = Rainfall.objects.filter(user=request.user)
    avg_rainfall = round(rainfall.aggregate(Avg('rainfall'))['rainfall__avg'] or '-', 2) if rainfall.aggregate(Avg('rainfall'))['rainfall__avg'] is not None else '-'

    moisture = MoistureMeasurement.objects.filter(crop__user=request.user)
    avg_moisture = round(moisture.aggregate(Avg('moisture'))['moisture__avg'], 2) if moisture.aggregate(Avg('moisture'))['moisture__avg'] is not None else '-'

    soil = SoilPh.objects.filter(crop__user=request.user)
    avg_soil = round(soil.aggregate(Avg('soil_ph'))['soil_ph__avg'] or '-', 2) if soil.aggregate(Avg('soil_ph'))['soil_ph__avg'] is not None else '-'

    # Listy do trzymiania wykresów
    moisture_bar_charts = []
    moisture_line_charts = []
    soil_ph_charts = []
    temperature_charts = []
    rainfall_charts = []

    if crops.exists():
        df = pd.DataFrame(list(crops.values('crop_name', 'area_ha')))
        if not df.empty:

            # Sumowanie danych o uprawach
            df_grouped = df.groupby('crop_name').sum().reset_index()

            # Tworzenie wykresu kołowego
            fig = px.pie(
                df_grouped,
                names='crop_name',
                values='area_ha',
                title='Udział poszczególnych plonów',
                color_discrete_sequence=px.colors.qualitative.Pastel,
            )
            fig.update_traces(textposition='inside', textinfo='percent+label')
            fig.update_layout(font=dict(family='Arial', size=12, color='#333333'))

            # Generowanie HTML
            pie_chart_html = fig.to_html(full_html=False)

            df = pd.DataFrame(list(crops.values('crop_name', 'yield_tons', 'area_ha')))
            df['yield_tons'] = pd.to_numeric(df['yield_tons'])
            df['area_ha'] = pd.to_numeric(df['area_ha'])
            df['yield_per_ha'] = (df['yield_tons'] / df['area_ha']).round(10)
            avg_yield = df.groupby('crop_name')['yield_per_ha'].mean().reset_index()

            # Tworzenie wykresu słupkowego
            fig = px.bar(
                avg_yield,
                x='crop_name',
                y='yield_per_ha',
                title='Średnia wydajność upraw',
                labels={'crop_name': '', 'yield_per_ha': 't/ha'},
                color='yield_per_ha',
                color_continuous_scale='Blues'
            )
            fig.update_layout(
                yaxis_title='t/ha',
                plot_bgcolor='white',
                paper_bgcolor='white',
                title_x=0.5,
                font=dict(family='Arial', size=12, color='#333333'),
                coloraxis_colorbar=dict(title='t/ha')
            )
            fig.update_yaxes(showgrid=True, gridcolor='lightgray')
            fig.update_xaxes(tickangle=45)

            avg_yield_chart_html = fig.to_html(full_html=False)
        else:
            pie_chart_html = None
            avg_yield_chart_html = None
    else:
        pie_chart_html = None
        avg_yield_chart_html = None

    for crop in crops:

        # Wilgotność
        moisture = crop.moisture_measurements.all().order_by('date')
        if moisture.exists():
            df = pd.DataFrame(list(moisture.values('date', 'moisture')))
            df['date'] = pd.to_datetime(df['date'])

            # Tworzenie wykresu słupkowego
            fig = px.bar(df, x='date',
                         y='moisture',
                         title=f'Wilgotność - {crop.crop_name}',
                         labels={'date': 'Data pomiaru', 'moisture': 'Wilgotność [%]'},
                         color='moisture',
                         color_continuous_scale='Blues'
                         )

            fig.update_layout(
                plot_bgcolor='white',
                paper_bgcolor='white',
                title_x=0.5,
                font=dict(family='Arial', size=12, color='#333333'),
                coloraxis_colorbar=dict(title='Wilgotność [%]')
            )
            fig.update_yaxes(showgrid=True, gridcolor='lightgray')
            fig.update_xaxes(tickformat='%d %b %Y', tickangle=45)
            moisture_bar_charts.append(fig.to_html(full_html=False))

            # Tworzenie wykresu liniowego
            fig = px.line(
                df,
                x='date',
                y='moisture',
                title=f'Wilgotność - {crop.crop_name}',
                labels={'date': 'Data pomiaru', 'moisture': 'Wilgotność [%]'},
                markers=True
            )
            fig.update_layout(
                plot_bgcolor='white',
                paper_bgcolor='white',
                title_x=0.5,
                font=dict(family='Arial', size=12, color='#333333')
            )
            fig.update_yaxes(showgrid=True, gridcolor='lightgray')
            fig.update_xaxes(tickformat='%d %b %Y', tickangle=45)
            moisture_line_charts.append(fig.to_html(full_html=False))

        # pH gleby
        soil_ph = crop.soil_phs.all().order_by('date')
        if soil_ph.exists():
            df = pd.DataFrame(list(soil_ph.values('date', 'soil_ph')))
            df['date'] = pd.to_datetime(df['date'])

            # Tworzenie wykresu słupkowego
            fig = px.bar(df, x='date',
                         y='soil_ph',
                         title=f'Ph gleby - {crop.crop_name}',
                         labels={'date': 'Data pomiaru', 'soil_ph': 'Ph'},
                         color='soil_ph',
                         color_continuous_scale='Viridis'
                         )

            fig.update_layout(
                plot_bgcolor='white',
                paper_bgcolor='white',
                title_x=0.5,
                font=dict(family='Arial', size=12, color='#333333'),
                coloraxis_colorbar=dict(title='Ph')
            )
            fig.update_yaxes(showgrid=True, gridcolor='lightgray')
            fig.update_xaxes(tickformat='%d %b %Y', tickangle=45)
            soil_ph_charts.append(fig.to_html(full_html=False))

            fig = px.area(
                df,
                x='date',
                y='soil_ph',
                title=f'Ph gleby - {crop.crop_name}',
                labels={'date': 'Data pomiaru', 'soil_ph': 'Ph gleby'},
                markers=True
            )
            fig.update_layout(
                plot_bgcolor='white',
                paper_bgcolor='white',
                title_x=0.5,
                font=dict(family='Arial', size=12, color='#333333')
            )
            fig.update_yaxes(showgrid=True, gridcolor='lightgray')
            fig.update_xaxes(tickformat='%d %b %Y', tickangle=45)
            soil_ph_charts.append(fig.to_html(full_html=False))


    # Temperatura
    temp = Temperature.objects.filter(user=request.user).order_by('date')
    if temp.exists():
        df = pd.DataFrame(list(temp.values('date', 'temperature')))
        df['date'] = pd.to_datetime(df['date'])

        # Tworzenie wykresu słupkowego
        fig = px.bar(df, x='date',
                     y='temperature',
                     title=f'Temperatura',
                     labels={'date': 'Data pomiaru', 'temperature': 'Temperatura [℃]'},
                     color='temperature',
                     color_continuous_scale='Blues'
                     )

        fig.update_layout(
            plot_bgcolor='white',
            paper_bgcolor='white',
            title_x=0.5,
            font=dict(family='Arial', size=12, color='#333333'),
            coloraxis_colorbar=dict(title='Temperatura [℃]')
        )
        fig.update_yaxes(showgrid=True, gridcolor='lightgray')
        fig.update_xaxes(tickformat='%d %b %Y', tickangle=45)
        temperature_charts.append(fig.to_html(full_html=False))

    # Opady
    rain = Rainfall.objects.filter(user=request.user).order_by('date')
    if rain.exists():
        df = pd.DataFrame(list(rain.values('date', 'rainfall')))

        # Tworzenie wykresu słupkowego
        fig = px.bar(df, x='date',
                     y='rainfall',
                     title=f'Opady',
                     labels = {'date': 'Data pomiaru', 'rainfall': 'Opady [mm]'},
                     color = 'rainfall',
                     color_continuous_scale = 'Blues'
                    )
        fig.update_layout(
            plot_bgcolor='white',
            paper_bgcolor='white',
            title_x=0.5,
            font=dict(family='Arial', size=12, color='#333333'),
            coloraxis_colorbar=dict(title='Opady [mm]')
        )
        fig.update_yaxes(showgrid=True, gridcolor='lightgray')
        fig.update_xaxes(tickformat='%d %b %Y', tickangle=45)
        rainfall_charts.append(fig.to_html(full_html=False))

    context = {
        'moisture_bar_charts': moisture_bar_charts,
        'moisture_line_charts': moisture_line_charts,
        'soil_ph_charts': soil_ph_charts,
        'temperature_charts': temperature_charts,
        'rainfall_charts': rainfall_charts,
        'pie_chart_html': pie_chart_html,
        'avg_yield_chart_html': avg_yield_chart_html,
        'total_area': total_area,
        'total_yields': total_yields,
        'avg_temperature': avg_temperature,
        'avg_rainfall': avg_rainfall,
        'avg_soil': avg_soil,
        'avg_moisture': avg_moisture,
    }

    return render(request, 'stats.html', context)

@login_required(login_url='login')
def crops(request):
    # Wyciąganie danych o uprawach, sortowanie po dacie siewu
    yields = Yield.objects.filter(user=request.user).order_by('sowing_date')
    return render(request, 'crops.html', {'yields': yields})

@login_required(login_url='login')
def crop_detail(request, pk):
    # Wyciąganie danych o uprawach, zabiegach, wilgotności i pH gleby
    crop = get_object_or_404(Yield, pk=pk, user=request.user)
    treatments = crop.treatments.all().order_by('date')
    moisture_measurements = crop.moisture_measurements.all().order_by('date')
    soil_phs = crop.soil_phs.all().order_by('date')
    return render(request, 'crop_detail.html', {
        'crop': crop,
        'treatments': treatments,
        'moisture_measurements': moisture_measurements,
        'soil_ph': soil_phs,
    })


@login_required(login_url='login')
def add_crops(request):
    # Sprawdzanie czy żądanie zostało wysłane metodą POST (formularz)
    if request.method == 'POST':
        # Tworzenie formularza
        form = YieldForm(request.POST, request.FILES)
        if form.is_valid():
            # Zapis danych do bazy dla odpowiedniego użytkownika
            new_yield = form.save(commit=False)
            new_yield.user = request.user
            new_yield.save()
            return redirect('crops')
    else:
        form = YieldForm()

    return render(request, 'add_crops.html', {'form': form})

@login_required(login_url='login')
def edit_crop(request, pk):
    # Pobranie obiektu Yield należącego do zalogowanego użytkownika
    # Jeśli rekord nie istnieje lub nie należy do użytkownika - zwraca błąd 404
    crop = get_object_or_404(Yield, pk=pk, user=request.user)
    # Sprawdzanie czy żądanie zostało wysłane metodą POST (formularz)
    if request.method == 'POST':
        # Tworzenie formularza
        form = YieldForm(request.POST, request.FILES ,instance=crop)
        if form.is_valid():
            # Zapis do bazy
            form.save()
            return redirect('crops')
    else:
        form = YieldForm(instance=crop)

    return render(request, 'edit_crop.html', {'form': form})

@login_required(login_url='login')
def delete_crop(request, pk):
    # Pobranie obiektu Yield należącego do zalogowanego użytkownika
    # Jeśli rekord nie istnieje lub nie należy do użytkownika - zwraca błąd 404
    crop = get_object_or_404(Yield, pk=pk, user=request.user)
    # Usunięcie z bazy
    crop.delete()
    return redirect('crops')

@login_required(login_url='login')
def add_moisture_measurement(request, pk):
    # Pobranie obiektu Yield należącego do zalogowanego użytkownika
    # Jeśli rekord nie istnieje lub nie należy do użytkownika - zwraca błąd 404
    crop = get_object_or_404(Yield, pk=pk, user=request.user)

    # Sprawdzanie czy żądanie zostało wysłane metodą POST
    if request.method == 'POST':
        # Tworzenie formularza
        form = MoistureMeasurementForm(request.POST)
        if form.is_valid():
            # Zapis do bazy dla odpowiedniej uprawy
            measurement = form.save(commit=False)
            measurement.crop = crop
            measurement.save()
            return redirect('crop_detail', pk=crop.pk)
    else:
        form = MoistureMeasurementForm()

    contex = {'crop': crop, 'form': form}

    return render(request, 'add_moisture_measurement.html', contex)

@login_required(login_url='login')
def edit_moisture_measurement(request, pk):
    # Pobranie obiektu MoistureMeasurement należącego do zalogowanego użytkownika
    # Jeśli rekord nie istnieje lub nie należy do użytkownika - zwraca błąd 404
    measurement = get_object_or_404(MoistureMeasurement, pk=pk, crop__user=request.user)

    # Sprawdzanie czy żądanie zostało wysłane metodą POST
    if request.method == 'POST':
        # Tworzenie formularza
        form = MoistureMeasurementForm(request.POST, instance=measurement)
        if form.is_valid():
            # Zapis do bazy
            form.save()
            return redirect('crop_detail', pk=measurement.crop.pk)
    else:
        form = MoistureMeasurementForm(instance=measurement)

    return render(request, 'edit_moisture_measurement.html', {'form': form, 'measurement': measurement})

@login_required(login_url='login')
def delete_moisture_measurement(request, pk):
    # Pobranie obiektu MoistureMeasurement należącego do zalogowanego użytkownika
    # Jeśli rekord nie istnieje lub nie należy do użytkownika - zwraca błąd 404
    measurement = get_object_or_404(MoistureMeasurement, pk=pk, crop__user=request.user)
    # id uprawy
    crop_id = measurement.crop.pk
    # Usuwanie z bazy
    measurement.delete()
    return redirect('crop_detail', pk=crop_id)


@login_required(login_url='login')
def add_treatment(request, pk):
    # Pobranie obiektu Yield należącego do zalogowanego użytkownika
    # Jeśli rekord nie istnieje lub nie należy do użytkownika - zwraca błąd 404
    crop = get_object_or_404(Yield, pk=pk, user=request.user)

    # Sprawdzanie czy żądanie zostało wysłane metodą POST
    if request.method == 'POST':
        # Tworzenie formularza
        form = TreatmentForm(request.POST)
        if form.is_valid():
            # Zapis do bazy dla odpowiedniej uprawy
            treatment = form.save(commit=False)
            treatment.yield_record = crop
            treatment.save()
            return redirect('crop_detail', pk=crop.pk)
    else:
        form = TreatmentForm()

    contex = {'crop': crop, 'form': form}
    return render(request, 'add_treatment.html', contex)

@login_required(login_url='login')
def edit_treatment(request, pk):
    # Pobranie obiektu Treatment należącego do zalogowanego użytkownika
    # Jeśli rekord nie istnieje lub nie należy do użytkownika - zwraca błąd 404
    treatment = get_object_or_404(Treatment, pk=pk, yield_record__user=request.user)

    # Sprawdzanie czy żądanie zostało wysłane metodą POST
    if request.method == 'POST':
        # Tworzenie formularza
        form = TreatmentForm(request.POST, instance=treatment)
        if form.is_valid():
            # Zapis do bazy
            form.save()
            return redirect('crop_detail', pk=treatment.yield_record.pk)
    else:
        form = TreatmentForm(instance=treatment)

    context = {'form': form, 'treatment': treatment}
    return render(request, 'edit_treatment.html', context)

@login_required(login_url='login')
def delete_treatment(request, pk):
    # Pobranie obiektu Treatment należącego do zalogowanego użytkownika
    # Jeśli rekord nie istnieje lub nie należy do użytkownika - zwraca błąd 404
    treatment = get_object_or_404(Treatment, pk=pk, yield_record__user=request.user)
    # id uprawy
    crop_id = treatment.yield_record.pk
    # Usuwanie z bazy
    treatment.delete()
    return redirect('crop_detail', pk=crop_id)

@login_required(login_url='login')
def add_soil_ph(request, pk):
    # Pobranie obiektu Yield należącego do zalogowanego użytkownika
    # Jeśli rekord nie istnieje lub nie należy do użytkownika - zwraca błąd 404
    crop = get_object_or_404(Yield, pk=pk, user=request.user)

    # Sprawdzanie czy żądanie zostało wysłane metodą POST
    if request.method == 'POST':
        # Tworzenie formularza
        form = SoilPhForm(request.POST)
        if form.is_valid():
            # Zapis do bazy dla odpowiedniej uprawy
            soil_ph = form.save(commit=False)
            soil_ph.crop = crop
            soil_ph.save()
            return redirect('crop_detail', pk=crop.pk)
    else:
        form = SoilPhForm()

    context = {'crop': crop, 'form': form}
    return render(request, 'add_soil_ph.html', context)

@login_required(login_url='login')
def edit_soil_ph(request, pk):
    # Pobranie obiektu SoilPh należącego do zalogowanego użytkownika
    # Jeśli rekord nie istnieje lub nie należy do użytkownika - zwraca błąd 404
    soil_ph = get_object_or_404(SoilPh, pk=pk, crop__user=request.user)

    # Sprawdzanie czy żądanie zostało wysłane metodą POST
    if request.method == 'POST':
        # Tworzenie formularza
        form = SoilPhForm(request.POST, instance=soil_ph)
        if form.is_valid():
            # Zapis do bazy
            form.save()
            return redirect('crop_detail', pk=soil_ph.crop.pk)
    else:
        form = SoilPhForm(instance=soil_ph)

    context = {'form': form, 'soil_ph': soil_ph}
    return render(request, 'edit_soil_ph.html', context)

@login_required(login_url='login')
def delete_soil_ph(request, pk):
    # Pobranie obiektu SoilPh należącego do zalogowanego użytkownika
    # Jeśli rekord nie istnieje lub nie należy do użytkownika - zwraca błąd 404
    soil_ph = get_object_or_404(SoilPh, pk=pk, crop__user=request.user)
    # id uprawy
    crop_id = soil_ph.crop.pk
    # Usuwanie z bazy
    soil_ph.delete()
    return redirect('crop_detail', pk=crop_id)


@login_required(login_url='login')
def add_temperature(request):
    # Sprawdzanie czy żądanie zostało wysłane metodą POST
    if request.method == 'POST':
        # Tworzenie formularza
        form = TemperatureForm(request.POST)
        if form.is_valid():
            # Dodawanie do bazy dla odpowiedniego użytkownika
            temperature = form.save(commit=False)
            temperature.user = request.user
            temperature.save()
            return redirect('weather')
    else:
        form = TemperatureForm()

    return render(request, 'add_temperature.html', {'form': form})

@login_required(login_url='login')
def edit_temperature(request, pk):
    # Pobranie obiektu Temperature należącego do zalogowanego użytkownika
    # Jeśli rekord nie istnieje lub nie należy do użytkownika - zwraca błąd 404
    temperature = get_object_or_404(Temperature, pk=pk)

    # Sprawdzanie czy żądanie zostało wysłane metodą POST
    if request.method == 'POST':
        # Tworzenie formularza
        form = TemperatureForm(request.POST, instance=temperature)
        if form.is_valid():
            # Zapis do bazy
            form.save()
            return redirect('weather')
    else:
        form = TemperatureForm(instance=temperature)

    return render(request, 'edit_temperature.html', {'form': form})


@login_required(login_url='login')
def delete_temperature(request, pk):
    # Pobranie obiektu Temperature należącego do zalogowanego użytkownika
    # Jeśli rekord nie istnieje lub nie należy do użytkownika - zwraca błąd 404
    temperature = get_object_or_404(Temperature, pk=pk)
    # Usuwanie z bazy
    temperature.delete()
    return redirect('weather')


@login_required(login_url='login')
def add_rainfall(request):
    # Sprawdzanie czy żadanie zostało wysłane metodą POST
    if request.method == 'POST':
        # Tworzenie formularza
        form = RainfallForm(request.POST)
        if form.is_valid():
            # Zapis do bazy dla odpowiedniego użytkownika
            rainfall = form.save(commit=False)
            rainfall.user = request.user
            rainfall.save()
            return redirect('weather')
    else:
        form = RainfallForm()

    return render(request, 'add_rainfall.html', {'form': form})

@login_required(login_url='login')
def edit_rainfall(request, pk):
    # Pobranie obiektu Rainfall należącego do zalogowanego użytkownika
    # Jeśli rekord nie istnieje lub nie należy do użytkownika - zwraca błąd 404
    rainfall = get_object_or_404(Rainfall, pk=pk)

    # Sprawdzanie czy żądanie zostało wysłane metodą POST
    if request.method == 'POST':
        form = RainfallForm(request.POST, instance=rainfall)
        if form.is_valid():
            # Zapis do bazy
            form.save()
            return redirect('weather')
    else:
        form = RainfallForm(instance=rainfall)

    return render(request, 'edit_rainfall.html', {'form': form})

@login_required(login_url='login')
def delete_rainfall(request, pk):
    # Pobranie obiektu Rainfall należącego do zalogowanego użytkownika
    # Jeśli rekord nie istnieje lub nie należy do użytkownika - zwraca błąd 404
    rainfall = get_object_or_404(Rainfall, pk=pk)
    # Usuwanie z bazy
    rainfall.delete()
    return redirect('weather')

@login_required(login_url='login')
def weather(request):
    API_KEY = settings.WEATHER_API_KEY
    weather = None

    # Sprawdzanie czy żądanie zostało wysłane metodą POST
    if request.method == "POST":
        city = request.POST.get('city')

        # Funkcja zamieniająca polskie znaki diakrytyczne
        def remove_polish_chars(text):
            replacements = {
                'ą': 'a', 'ć': 'c', 'ę': 'e', 'ł': 'l', 'ń': 'n', 'ó': 'o', 'ś': 's', 'ź': 'z', 'ż': 'z',
                'Ą': 'A', 'Ć': 'C', 'Ę': 'E', 'Ł': 'L', 'Ń': 'N', 'Ó': 'O', 'Ś': 'S', 'Ź': 'Z', 'Ż': 'Z'
            }
            return ''.join(replacements.get(c, c) for c in text)

        city_ascii = remove_polish_chars(city)

        # Wykonanie połączenia API
        if city_ascii:
            try:
                url = "http://api.weatherapi.com/v1/current.json"
                params = {
                    "key": API_KEY,
                    "q": city_ascii,
                    "aqi": "no",
                    "lang": "pl"
                }
                response = requests.get(url, params=params)
                if response.status_code == 200:
                    weather = response.json()
                else:
                    print("Błąd API:", response.status_code, response.text)
            except requests.exceptions.RequestException as e:
                print("Błąd połączenia:", e)

    # Wyciąganie danych z bazy (wykorzystywane do przekazania ich do template)
    temperature = Temperature.objects.filter(user=request.user).order_by('date')
    rainfall = Rainfall.objects.filter(user=request.user).order_by('date')

    context = {'temperature': temperature, 'rainfall': rainfall, 'weather': weather}
    return render(request, 'weather.html', context)


@login_required(login_url='login')
def reports(request):
    # Tworzenie formularza
    form = ReportsForm(user=request.user)

    # Sprawdzanie czy żądanie zostało wysłane metodą POST
    if request.method == 'POST':
        # Tworzenie formularza
        form = ReportsForm(request.POST, user=request.user)
        if form.is_valid():
            # Dane dodatkowe (obraz i aktualna data)
            logo_path = request.build_absolute_uri(static('logo_svg.svg'))
            current_date = now()

            # Wyciąganie danych z formularza
            crop = form.cleaned_data['crop']
            include_treatments = form.cleaned_data['include_treatments']
            include_moisture = form.cleaned_data['include_moisture']
            include_soil_ph = form.cleaned_data['include_soil_ph']
            include_temperature = form.cleaned_data['include_temperature']
            include_rainfall = form.cleaned_data['include_rainfall']

            context = {
                'logo_path': logo_path,
                'current_date': current_date,
                'crop': crop,
                'include_treatments': include_treatments,
                'include_moisture': include_moisture,
                'include_soil_ph': include_soil_ph,
                'include_temperature': include_temperature,
                'include_rainfall': include_rainfall,
            }

            # Tworzenie pdf na podstawie template
            html_string = render_to_string('report_pdf_template.html', context)
            html = HTML(string=html_string)
            pdf = html.write_pdf()
            response = HttpResponse(pdf, content_type='application/pdf')
            response['Content-Disposition'] = f'attachment; filename="raport_{crop.crop_name}.pdf"'
            return response
    else:
        form = ReportsForm(user=request.user)

    return render(request, 'reports.html', {'form': form})


@login_required(login_url='login')
def export_crops_csv(request):
    response = HttpResponse(content_type='text/csv', headers={'Content-Disposition': 'attachment; filename="my_crops.csv"'},)

    # Obiekt zapisujący do csv
    writer = csv.writer(response)
    response.write('\ufeff'.encode('utf8'))

    # Nagłówki kolumn
    writer.writerow(['Nazwa', 'Lokalizacja', 'Obszar (ha)', 'Ilość zebranych plonów (tony)', 'Data siewu', 'Data zbioru', 'Zabiegi'])

    # Pobranie wszystkich danych dla użytkownika
    crops = Yield.objects.filter(user=request.user).order_by('sowing_date')

    # Iteracja po wszystkich uprawach
    for crop in crops:
        treatments = crop.treatments.all().filter(yield_record__user=request.user).order_by('date')
        treatment_descriptions = "; ".join([f"{t.date} {t.name} ({t.amount})" for t in treatments])
        writer.writerow([crop.crop_name, crop.location, crop.area_ha, crop.yield_tons, crop.sowing_date, crop.harvest_date, treatment_descriptions])

    return response

@login_required(login_url='login')
def export_crops_pdf(request):
    # Pobranie logo ze staticow
    logo_path = request.build_absolute_uri(static('logo_svg.svg'))

    # Pobranie danych o użytkowniku
    username = request.user.username
    user_email = request.user.email

    # Pobranie danych z bazy o uprawach
    crops = Yield.objects.filter(user=request.user).order_by('sowing_date')
    current_date = now()

    context = {'logo_path': logo_path, 'crops': crops, 'current_date': current_date, 'username': username, 'user_email': user_email}

    # Tworzenie pdf na podstawie template
    html_string = render_to_string('my_crops_pdf_template.html', context)
    html = HTML(string=html_string)
    pdf_file = html.write_pdf()

    response = HttpResponse(pdf_file, content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="my_crops.pdf"'

    return response


