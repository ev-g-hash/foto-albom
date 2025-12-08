from django.shortcuts import render, get_object_or_404, redirect
from django.core.paginator import Paginator
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth import authenticate, login, logout
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from django.shortcuts import get_object_or_404
import base64
import json
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
    """Страница содержания с кнопкой загрузки (только для суперюзера)"""
    photos = Photo.objects.all()
    can_upload = request.user.is_authenticated and request.user.is_superuser
    return render(request, 'conclusion.html', {
        'photos': photos, 
        'can_upload': can_upload
    })

def is_superuser(user):
    """Проверка на суперюзера"""
    return user.is_authenticated and user.is_superuser

@user_passes_test(is_superuser)
def upload_photos(request):
    """Страница загрузки фотографий (только для суперюзера)"""
    if request.method == 'POST':
        # Обработка AJAX загрузки
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return handle_ajax_upload(request)
        
        # Обычная обработка формы
        return handle_regular_upload(request)
    
    return render(request, 'upload.html')

@csrf_exempt
@require_http_methods(["POST"])
@user_passes_test(is_superuser)
def handle_ajax_upload(request):
    """AJAX обработка загрузки файлов (только для суперюзера)"""
    try:
        # Получаем данные из запроса
        data = json.loads(request.body)
        image_data = data.get('image')
        title = data.get('title', '')
        description = data.get('description', '')
        
        if not image_data:
            return JsonResponse({'success': False, 'error': 'Изображение не получено'})
        
        # Декодируем base64 изображение
        if ',' in image_data:
            header, image_data = image_data.split(',', 1)
        
        # Генерируем имя файла
        import uuid
        filename = f"photo_{uuid.uuid4().hex[:8]}.jpg"
        
        # Сохраняем файл
        image_content = ContentFile(base64.b64decode(image_data))
        photo = Photo.objects.create(
            title=title,
            description=description,
            image=image_content
        )
        
        return JsonResponse({
            'success': True, 
            'message': 'Фото успешно загружено!',
            'photo_id': photo.id,
            'photo_url': photo.image.url
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False, 
            'error': f'Ошибка при загрузке: {str(e)}'
        })

@user_passes_test(is_superuser)
def handle_regular_upload(request):
    """Обработка обычной загрузки через форму (только для суперюзера)"""
    try:
        images = request.FILES.getlist('images')
        title = request.POST.get('title', '')
        description = request.POST.get('description', '')
        
        uploaded_count = 0
        for image in images:
            # Валидация файла
            if not image.content_type.startswith('image/'):
                messages.error(request, f'Файл {image.name} не является изображением')
                continue
                
            if image.size > 5 * 1024 * 1024:  # 5MB
                messages.error(request, f'Файл {image.name} слишком большой (макс. 5MB)')
                continue
            
            Photo.objects.create(
                title=title or image.name,
                description=description,
                image=image
            )
            uploaded_count += 1
        
        if uploaded_count > 0:
            messages.success(request, f'Успешно загружено {uploaded_count} фото!')
        else:
            messages.error(request, 'Не удалось загрузить фотографии')
            
        return redirect('conclusion')  # Перенаправляем на содержание
        
    except Exception as e:
        messages.error(request, f'Ошибка при загрузке: {str(e)}')
        return render(request, 'upload.html')

@csrf_exempt
@require_http_methods(["POST"])
@user_passes_test(is_superuser)
def delete_photo(request, pk):
    """Удаление фотографии (только для суперюзера)"""
    try:
        photo = get_object_or_404(Photo, pk=pk)
        photo.delete()
        return JsonResponse({'success': True, 'message': 'Фотография удалена'})
    except Exception as e:
        return JsonResponse({'success': False, 'error': f'Ошибка при удалении: {str(e)}'})

# =============================================================================
# СИСТЕМА АВТОРИЗАЦИИ
# =============================================================================

def user_login(request):
    """Страница входа"""
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            if user.is_superuser:
                login(request, user)
                messages.success(request, 'Вы успешно вошли в систему!')
                return redirect('conclusion')
            else:
                messages.error(request, 'У вас нет прав администратора')
        else:
            messages.error(request, 'Неверное имя пользователя или пароль')
    
    return render(request, 'login.html')

@login_required
def user_logout(request):
    """Выход из системы"""
    logout(request)
    messages.success(request, 'Вы успешно вышли из системы')
    return redirect('greeting')