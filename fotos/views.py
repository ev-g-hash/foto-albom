from django.shortcuts import render, get_object_or_404
from django.core.paginator import Paginator
from .models import Photo

def greeting(request):
    """Главная страница с поздравлением"""
    return render(request, 'greeting.html')

def gallery(request):
    photos_list = Photo.objects.all()
    
    # Определяем количество фото на странице (по умолчанию 3 для десктопа)
    # JavaScript будет корректировать это для мобильных
    per_page = request.GET.get('per_page', 3)
    
    paginator = Paginator(photos_list, per_page)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(request, 'gallery.html', {'page_obj': page_obj, 'per_page': per_page})

def photo_detail(request, pk: int):
    photo = get_object_or_404(Photo, pk=pk)
    return render(request, 'detail.html', {'photo': photo})

def conclusion(request):
    photos = Photo.objects.all()
    return render(request, 'conclusion.html', {'photos': photos})