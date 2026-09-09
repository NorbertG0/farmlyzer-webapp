from pymeter.api import ContentType
from pymeter.api.config import TestPlan, ThreadGroupWithRampUpAndHold
from pymeter.api.reporters import HtmlReporter
from pymeter.api.samplers import HttpSampler


test_profiles = [
    # {'threads': 10, 'rampups': 10, 'hold': 30},
    #{'threads': 50, 'rampups': 50, 'hold': 300},
    {'threads': 100, 'rampups': 100, 'hold': 600},
]

# Endpointy dostepne dla gosci (niezalogowanych uzytkownikow)
home_page = HttpSampler('home page', 'http://127.0.0.1:8000/')
register = HttpSampler('register', 'http://127.0.0.1:8000/register/')
login_page = HttpSampler('login page', 'http://127.0.0.1:8000/login/')
reset_pass = HttpSampler('reset password', 'http://127.0.0.1:8000/reset_password/')

# Logowanie
login = ((HttpSampler('login','http://127.0.0.1:8000/login/')
         .post({"username": "test", "password": "asdweragfv"}, ContentType.APPLICATION_FORM_URLENCODED))
         .header("Content-Type", "application/x-www-form-urlencoded; charset=utf-8"))


user_edit = HttpSampler('user edit', 'http://127.0.0.1:8000/user/edit/')
dashboard = HttpSampler("dashboard", "http://127.0.0.1:8000/dashboard/")
crops = HttpSampler("crops", "http://127.0.0.1:8000/dashboard/crops/")
stats = HttpSampler("stats", "http://127.0.0.1:8000/dashboard/stats/")
weather = HttpSampler("weather", "http://127.0.0.1:8000/dashboard/weather/")
reports = HttpSampler("reports", "http://127.0.0.1:8000/dashboard/reports/")


# Endpointy dostepne dla zalogowanych uzytkownikow

for profile in test_profiles:
    thread_group = ThreadGroupWithRampUpAndHold(
        profile['threads'],
        profile['rampups'],
        profile['hold'],
        home_page,
        register,
        login_page,
        reset_pass,
        login,
        user_edit,
        dashboard,
        crops,
        stats,
        weather,
        reports,
    )

html_reporter = HtmlReporter()
test_plan = TestPlan( thread_group, html_reporter)
stats = test_plan.run()