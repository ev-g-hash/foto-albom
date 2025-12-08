from django.urls import path
from . import views

urlpatterns = [
    path('', views.greeting, name='greeting'),  # Главная страница
    path('fotos/', views.gallery, name='gallery'),
    path('fotos/upload/', views.upload_photos, name='upload_photos'),  # Только для суперюзера
    path('fotos/delete/<int:pk>/', views.delete_photo, name='delete_photo'),  # Удаление
    path('fotos/conclusion/', views.conclusion, name='conclusion'),
    path('fotos/<int:pk>/', views.photo_detail, name='photo_detail'),
]