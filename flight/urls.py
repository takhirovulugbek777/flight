from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views2 import *

urlpatterns = [

    path('all/', AllFlightsDetailApiView.as_view(), name='unique-flights'),
    path('category/<str:departure_airport>/', CategoryFlightsDetailApiView.as_view(), name='unique-flights'),

]
