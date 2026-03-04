from django.urls import path

from . import views


app_name = "calculator"

urlpatterns = [
    path("", views.index, name="index"),
    path("api/calculate/", views.calculate_api, name="calculate_api"),
]

