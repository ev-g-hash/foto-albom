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
from PIL import Image, ImageOps
import io
import base64
import json
import os 
from .models import Photo

def greeting(request):
    """Главная страница с поздравлением"""
    return render(request, 'greeting.html')

def gallery(request):
    photos_list = Photo.objects.all()
    
    # ВСЕГДА показываем по 3 фото на странице (убрали адаптивность)
    per_page = 6
    
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

def compress_image(image_file, max_width=1920, max_height=1080, quality=85):
    """
    Сжимает изображение до указанных размеров с оптимизацией качества
    Оптимизировано для Amvera (ограниченные ресурсы)
    """
    try:
        # Открываем изображение
        img = Image.open(image_file)
        
        # Конвертируем в RGB если нужно (для JPEG)
        if img.mode in ('RGBA', 'LA', 'P'):
            # Создаём белый фон для прозрачных изображений
            background = Image.new('RGB', img.size, (255, 255, 255))
            if img.mode == 'P':
                img = img.convert('RGBA')
            background.paste(img, mask=img.split()[-1] if img.mode == 'RGBA' else None)
            img = background
        elif img.mode != 'RGB':
            img = img.convert('RGB')
        
        # Поворачиваем если нужно (EXIF данные)
        img = ImageOps.exif_transpose(img)
        
        # Получаем текущие размеры
        width, height = img.size
        
        # Вычисляем новые размеры (сохраняем пропорции)
        if width > max_width or height > max_height:
            img.thumbnail((max_width, max_height), Image.Resampling.LANCZOS)
        
        # Сохраняем в буфер с оптимизацией
        img_io = io.BytesIO()
        img.save(
            img_io, 
            format='JPEG', 
            quality=quality, 
            optimize=True,
            progressive=True
        )
        img_io.seek(0)
        
        return img_io, img.size
        
    except Exception as e:
        raise ValueError(f"Ошибка обработки изображения: {str(e)}")

def create_thumbnail(image_io, size=(300, 300), quality=80):
    """Создаёт превью изображение"""
    try:
        img = Image.open(image_io)
        img.thumbnail(size, Image.Resampling.LANCZOS)
        
        thumb_io = io.BytesIO()
        img.save(
            thumb_io, 
            format='JPEG', 
            quality=quality, 
            optimize=True
        )
        thumb_io.seek(0)
        
        return thumb_io
        
    except Exception as e:
        raise ValueError(f"Ошибка создания превью: {str(e)}")

@csrf_exempt
@require_http_methods(["POST"])
@user_passes_test(is_superuser)
def handle_ajax_upload(request):
    """AJAX обработка загрузки файлов (только для суперюзера) с сжатием"""
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
        
        # Создаём временный файл для обработки
        import uuid
        temp_filename = f"temp_{uuid.uuid4().hex[:8]}.jpg"
        temp_image = ContentFile(base64.b64decode(image_data))
        temp_image.name = temp_filename
        
        # Сжимаем изображение
        compressed_io, final_size = compress_image(temp_image)
        
        # Создаём финальный файл
        final_filename = f"photo_{uuid.uuid4().hex[:8]}.jpg"
        final_image = ContentFile(compressed_io.read())
        final_image.name = final_filename
        
        # Сохраняем в базу
        photo = Photo.objects.create(
            title=title,
            description=description,
            image=final_image
        )
        
        # Создаём превью
        compressed_io.seek(0)
        thumbnail_io = create_thumbnail(compressed_io)
        thumbnail_name = f"thumb_{photo.id}.jpg"
        thumbnail_content = ContentFile(thumbnail_io.read())
        thumbnail_content.name = thumbnail_name
        
        # Можно сохранить превью отдельно если нужно
        # photo.thumbnail = thumbnail_content
        # photo.save()
        
        return JsonResponse({
            'success': True, 
            'message': f'Фото успешно загружено и сжато до {final_size[0]}x{final_size[1]}!',
            'photo_id': photo.id,
            'photo_url': photo.image.url,
            'size': f"{final_size[0]}x{final_size[1]}"
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False, 
            'error': f'Ошибка при загрузке: {str(e)}'
        })

@user_passes_test(is_superuser)
def handle_regular_upload(request):
    """Обработка обычной загрузки через форму (только для суперюзера) с сжатием"""
    try:
        images = request.FILES.getlist('images')
        title = request.POST.get('title', '')
        description = request.POST.get('description', '')
        
        uploaded_count = 0
        total_saved_mb = 0
        
        for image in images:
            # Валидация файла
            if not image.content_type.startswith('image/'):
                messages.error(request, f'Файл {image.name} не является изображением')
                continue
                
            if image.size > 20 * 1024 * 1024:  # 20MB максимум
                messages.error(request, f'Файл {image.name} слишком большой (макс. 20MB)')
                continue
            
            try:
                # Сжимаем изображение
                compressed_io, final_size = compress_image(image)
                
                # Создаём финальный файл
                import uuid
                final_filename = f"photo_{uuid.uuid4().hex[:8]}.jpg"
                final_image = ContentFile(compressed_io.read())
                final_image.name = final_filename
                
                # Сохраняем в базу
                photo = Photo.objects.create(
                    title=title or image.name,
                    description=description,
                    image=final_image
                )
                
                uploaded_count += 1
                
                # Подсчитываем сэкономленное место
                original_mb = image.size / (1024 * 1024)
                final_mb = len(compressed_io.getvalue()) / (1024 * 1024)
                total_saved_mb += (original_mb - final_mb)
                
            except Exception as e:
                messages.error(request, f'Ошибка обработки файла {image.name}: {str(e)}')
                continue
        
        if uploaded_count > 0:
            saved_mb_str = f" (сэкономлено {total_saved_mb:.1f} МБ)" if total_saved_mb > 0 else ""
            messages.success(request, f'Успешно загружено и сжато {uploaded_count} фото{saved_mb_str}!')
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
        photo_title = photo.title or f"Фото #{photo.pk}"
        photo.delete()
        
        return JsonResponse({
            'success': True, 
            'message': f'Фотография "{photo_title}" успешно удалена!'
        })
    except Exception as e:
        return JsonResponse({
            'success': False, 
            'error': f'Ошибка при удалении: {str(e)}'
        })

# =============================================================================
# НОВАЯ ФУНКЦИЯ РЕДАКТИРОВАНИЯ ФОТО
# =============================================================================

@csrf_exempt
@require_http_methods(["POST"])
@user_passes_test(is_superuser)
def edit_photo(request, pk):
    """Редактирование фотографии (только для суперюзера)"""
    try:
        photo = get_object_or_404(Photo, pk=pk)
        
        # Получаем данные из запроса
        data = json.loads(request.body)
        field = data.get('field')
        value = data.get('value', '')
        
        if field == 'title':
            photo.title = value
            photo.save()
            return JsonResponse({
                'success': True, 
                'message': 'Название успешно обновлено!'
            })
        elif field == 'description':
            photo.description = value
            photo.save()
            return JsonResponse({
                'success': True, 
                'message': 'Описание успешно обновлено!'
            })
        else:
            return JsonResponse({
                'success': False, 
                'error': 'Неподдерживаемое поле'
            })
            
    except Exception as e:
        return JsonResponse({
            'success': False, 
            'error': f'Ошибка при редактировании: {str(e)}'
        })

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