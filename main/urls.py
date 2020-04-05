from django.urls import path
from . import views

urlpatterns = [
    path('main/',views.MainApp),
    path('main/convert/',views.Show),

]