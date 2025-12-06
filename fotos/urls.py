from django.urls import path
from . import views

urlpatterns = [
    path('', views.greeting, name='greeting'),  # Главная страница
    path('fotos/', views.gallery, name='gallery'),
    path('fotos/conclusion/', views.conclusion, name='conclusion'),
    path('fotos/<int:pk>/', views.photo_detail, name='photo_detail'),
]