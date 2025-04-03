from django.urls import path
from .views import extract_pdf

urlpatterns = [
    path('extract/', extract_pdf, name='extract_pdf'),
]
