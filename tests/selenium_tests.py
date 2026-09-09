from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select

import string
import time
import secrets

from selenium.webdriver.support.wait import WebDriverWait


def generate_username(prefix="user", length=6):
    alphabet = string.ascii_lowercase + string.digits + string.ascii_uppercase
    result = ''.join(secrets.choice(alphabet) for _ in range(length))
    return f"{prefix}{result}"

def generate_password(length=10):
    alphabet = string.ascii_lowercase + string.digits + string.ascii_uppercase
    result = ''.join(secrets.choice(alphabet) for _ in range(length))
    return f"{result}"

def generate_email(length=6):
    alphabet = string.ascii_lowercase + string.digits + string.ascii_uppercase
    result = ''.join(secrets.choice(alphabet) for _ in range(length))+"@test.com"
    return f"{result}"


driver = webdriver.Chrome()


def register_test():
    for _ in range(50):
        driver.get('http://localhost:8000/register/')
        WebDriverWait(driver, 15).until(
            EC.text_to_be_present_in_element((By.TAG_NAME, 'body'), 'Rejestracja')
        )
        username = driver.find_element(By.NAME, 'username')
        username.clear()
        username.send_keys(generate_username())

        email = driver.find_element(By.NAME, 'email')
        email.clear()
        email.send_keys(generate_email())

        password1 = driver.find_element(By.NAME, 'password1')
        password1.clear()
        passwd = generate_password()
        password1.send_keys(passwd)

        password2 = driver.find_element(By.NAME, 'password2')
        password2.clear()
        password2.send_keys(passwd)

        register_button = driver.find_element(By.XPATH, "//button[text()='Zarejestruj się']")
        register_button.click()

        WebDriverWait(driver, 15).until(
            EC.url_contains('/dashboard/')
        )

        assert 'Panel główny' in driver.page_source, 'Rejestracja nie powiodła się!'

def login_test():
    driver.get('http://localhost:8000/login/')
    WebDriverWait(driver, 15).until(
        EC.text_to_be_present_in_element((By.TAG_NAME, 'body'), 'Logowanie')
    )

    username = driver.find_element(By.NAME, 'username')
    username.clear()
    username.send_keys('test')

    password = driver.find_element(By.NAME, 'password')
    password.clear()
    password.send_keys('asdweragfv')

    login_button = WebDriverWait(driver, 15).until(
        EC.element_to_be_clickable((By.XPATH, "//button[text()='Zaloguj się']"))
    )
    driver.execute_script("arguments[0].click();", login_button)

    WebDriverWait(driver, 15).until(
        EC.url_contains('/dashboard/')
    )

    assert 'Panel główny' in driver.page_source, 'Logowanie nie powiodlo sie'

def reset_pass_test():
    driver.get('http://localhost:8000/reset_password/')

    email = driver.find_element(By.NAME, 'email')
    email.send_keys('test@test.pl')

    send_button = WebDriverWait(driver, 15).until(
        EC.element_to_be_clickable((By.XPATH, "//button[text()='Wyślij!']"))
    )
    driver.execute_script("arguments[0].click();", send_button)

    WebDriverWait(driver, 15).until(
        EC.url_contains('/reset_password_sent/')
    )

    assert 'Email został wysłany!' in driver.page_source, 'Resetowanie hasla nie powiodlo sie'

def add_crop_test():
    login_test()

    driver.get('http://localhost:8000/dashboard/crops/add')

    crop_name = driver.find_element(By.NAME, 'crop_name')
    crop_name.clear()
    crop_name.send_keys('test')

    area = driver.find_element(By.NAME, 'area_ha')
    area.clear()
    area.send_keys('21')

    yield_tons = driver.find_element(By.NAME, 'yield_tons')
    yield_tons.clear()
    yield_tons.send_keys('21')

    sowing_method = driver.find_element(By.NAME, 'sowing_method')
    select = Select(sowing_method)
    select.select_by_index(1)

    sowing_date = driver.find_element(By.NAME, 'sowing_date')
    sowing_date.clear()
    sowing_date.send_keys('27-10-2025')

    harvest_date = driver.find_element(By.NAME, 'harvest_date')
    harvest_date.clear()
    harvest_date.send_keys('27-10-2025')

    location = driver.find_element(By.NAME, 'location')
    location.clear()
    location.send_keys('test')

    previous_crop = driver.find_element(By.NAME, 'previous_crop')
    previous_crop.clear()
    previous_crop.send_keys('test')

    add_button = WebDriverWait(driver, 15).until(
        EC.element_to_be_clickable((By.XPATH, "//button[text()='Dodaj']"))
    )
    driver.execute_script("arguments[0].click();", add_button)

    WebDriverWait(driver, 15).until(
        EC.url_contains('/dashboard/crops')
    )

    assert 'Moje uprawy' in driver.page_source, 'Dodawanie nie powiodlo sie'

def edit_crop_test(crop_id):
    login_test()

    driver.get(f'http://localhost:8000/dashboard/crops/edit/{crop_id}')

    crop_name = driver.find_element(By.NAME, 'crop_name')
    crop_name.clear()
    crop_name.send_keys('new crop name')

    area = driver.find_element(By.NAME, 'area_ha')
    area.clear()
    area.send_keys('2,2')

    yield_tons = driver.find_element(By.NAME, 'yield_tons')
    yield_tons.clear()
    yield_tons.send_keys('2,2')

    sowing_method = driver.find_element(By.NAME, 'sowing_method')
    select = Select(sowing_method)
    select.select_by_index(2)

    sowing_date = driver.find_element(By.NAME, 'sowing_date')
    sowing_date.clear()
    sowing_date.send_keys('11-05-2000')

    harvest_date = driver.find_element(By.NAME, 'harvest_date')
    harvest_date.clear()
    harvest_date.send_keys('11-05-2000')

    location = driver.find_element(By.NAME, 'location')
    location.clear()
    location.send_keys('new location')

    previous_crop = driver.find_element(By.NAME, 'previous_crop')
    previous_crop.clear()
    previous_crop.send_keys('new previous crop')

    add_button = WebDriverWait(driver, 15).until(
        EC.element_to_be_clickable((By.XPATH, "//button[text()='Zapisz zmiany']"))
    )
    driver.execute_script("arguments[0].click();", add_button)

    WebDriverWait(driver, 15).until(
        EC.url_contains('/dashboard/crops')
    )

    assert 'Moje uprawy' in driver.page_source, 'Edycja nie powiodla sie'

def delete_crop_test(crop_id):
    login_test()

    driver.get(f'http://localhost:8000/dashboard/crops/delete/{crop_id}')

    WebDriverWait(driver, 15).until(
        EC.url_contains('/dashboard/crops')
    )

    assert 'Moje uprawy' in driver.page_source, 'Usuwanie nie powiodlo sie'

def add_treatment_test(crop_id):
    login_test()

    driver.get(f'http://localhost:8000/dashboard/crops/add_treatment/{crop_id}/')

    treatment_type = driver.find_element(By.NAME, 'treatment_type')
    select = Select(treatment_type)
    select.select_by_index(1)

    treatment_name = driver.find_element(By.NAME, 'name')
    treatment_name.clear()
    treatment_name.send_keys('test')

    amount = driver.find_element(By.NAME, 'amount')
    amount.clear()
    amount.send_keys('21')

    treatment_date = driver.find_element(By.NAME, 'date')
    treatment_date.clear()
    treatment_date.send_keys('27-10-2025')

    save_button = WebDriverWait(driver, 15).until(
        EC.element_to_be_clickable((By.XPATH, "//button[text()='Zapisz']"))
    )
    driver.execute_script("arguments[0].click();", save_button)

    WebDriverWait(driver, 15).until(
        EC.url_contains(f'/dashboard/crops/{crop_id}')
    )

    assert 'Informacje' in driver.page_source, 'Dodawanie zabiegu nie powiodlo sie'

def edit_treatment_test(crop_id):
    login_test()

    driver.get(f'http://localhost:8000/dashboard/crops/edit_treatment/{crop_id}/')

    treatment_type = driver.find_element(By.NAME, 'treatment_type')
    select = Select(treatment_type)
    select.select_by_index(2)

    treatment_name = driver.find_element(By.NAME, 'name')
    treatment_name.clear()
    treatment_name.send_keys('new treatment name')

    amount = driver.find_element(By.NAME, 'amount')
    amount.clear()
    amount.send_keys('2,3')

    treatment_date = driver.find_element(By.NAME, 'date')
    treatment_date.clear()
    treatment_date.send_keys('27-08-2020')

    time.sleep(5)

    save_button = WebDriverWait(driver, 15).until(
        EC.element_to_be_clickable((By.XPATH, "//button[text()='Zapisz zmiany']"))
    )
    driver.execute_script("arguments[0].click();", save_button)

    WebDriverWait(driver, 15).until(
        EC.url_contains(f'/dashboard/crops/{crop_id}')
    )

    assert 'Informacje' in driver.page_source, 'Edycja danych zabiegu nie powiodla sie'

def delete_treatment_test(treatment_id):
    login_test()

    driver.get(f'http://localhost:8000/dashboard/crops/delete_treatment/{treatment_id}/')

def add_temperature_test():
    login_test()

    driver.get(f'http://localhost:8000/dashboard/weather/add_temperature/')

    date = driver.find_element(By.NAME, 'date')
    date.clear()
    date.send_keys('27-10-2025')

    temperature = driver.find_element(By.NAME, 'temperature')
    temperature.clear()
    temperature.send_keys('21,5')

    save_button = WebDriverWait(driver, 15).until(
        EC.element_to_be_clickable((By.XPATH, "//button[text()='Zapisz']"))
    )
    driver.execute_script("arguments[0].click();", save_button)

    WebDriverWait(driver, 15).until(
        EC.url_contains(f'/dashboard/weather/')
    )

    assert 'Pogoda' in driver.page_source, 'Dodawanie pomiaru temperatury nie powiodlo sie'

def edit_temperature_test(measurement_id):
    login_test()

    driver.get(f'http://localhost:8000/dashboard/weather/edit_temperature/{measurement_id}/')

    date = driver.find_element(By.NAME, 'date')
    date.clear()
    date.send_keys('22-12-2022')

    temperature = driver.find_element(By.NAME, 'temperature')
    temperature.clear()
    temperature.send_keys('10,8')

    save_button = WebDriverWait(driver, 15).until(
        EC.element_to_be_clickable((By.XPATH, "//button[text()='Zapisz zmiany']"))
    )
    driver.execute_script("arguments[0].click();", save_button)

    WebDriverWait(driver, 15).until(
        EC.url_contains(f'/dashboard/weather/')
    )

    assert 'Pogoda' in driver.page_source, 'Edycja pomiaru temperatury nie powiodla sie'

def delete_temperature_test(measurement_id):
    login_test()

    driver.get(f'http://localhost:8000/dashboard/weather/delete_temperature/{measurement_id}/')


# add_crop_test()
# reset_pass_test()
# edit_crop_test()
# delete_crop_test(5)
# add_treatment_test(2)
# edit_treatment_test(2)
# delete_treatment_test(3)
# add_temperature_test()
# edit_temperature_test(2)
# delete_temperature_test(1)
driver.close()