from django.urls import path
from . import views

urlpatterns = [
    path('',views.MainApp),
    path('convert/',views.Show),

]