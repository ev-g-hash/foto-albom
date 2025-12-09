from django.db import models
import os
import uuid
from PIL import Image
from django.core.exceptions import ValidationError

def photo_upload_path(instance, filename):
    """Генерирует путь для сохранения файла с оптимизированным именем"""
    # Получаем расширение файла
    ext = filename.split('.')[-1].lower()
    
    # Все изображения сохраняем как JPG для оптимизации
    if ext not in ['jpg', 'jpeg', 'png', 'webp']:
        ext = 'jpg'
    
    # Если у объекта есть ID, используем его, иначе генерируем временный
    if instance.pk:
        filename_base = str(instance.pk)
    else:
        # Для новых объектов используем UUID
        filename_base = f"temp_{uuid.uuid4().hex[:8]}"
    
    # Возвращаем путь с оптимизированным именем
    return os.path.join('photos/', f"{filename_base}.jpg")

def validate_image_size(image):
    """Валидация размера изображения"""
    max_size = 20 * 1024 * 1024  # 20MB
    if image.size > max_size:
        raise ValidationError(f'Размер файла не должен превышать 20MB')

def validate_image_dimensions(image):
    """Валидация размеров изображения"""
    try:
        img = Image.open(image)
        width, height = img.size
        
        # Проверяем максимальные размеры
        if width > 8000 or height > 8000:
            raise ValidationError('Размер изображения не должен превышать 8000x8000 пикселей')
        
        # Проверяем минимальные размеры
        if width < 100 or height < 100:
            raise ValidationError('Размер изображения должен быть не менее 100x100 пикселей')
            
    except Exception:
        raise ValidationError('Неподдерживаемый формат изображения')

class Photo(models.Model):
    title = models.CharField('Название', max_length=200, blank=True)
    description = models.TextField('Описание', blank=True)
    image = models.ImageField(
        'Изображение', 
        upload_to=photo_upload_path,
        validators=[validate_image_size, validate_image_dimensions]
    )
    created_at = models.DateTimeField('Дата создания', auto_now_add=True)
    
    # Поле для превью (опционально)
    thumbnail = models.ImageField('Превью', upload_to='thumbnails/', blank=True, null=True)

    class Meta:
        ordering = ['id'] 
        verbose_name = 'Фото'
        verbose_name_plural = 'Фотографии'

    def __str__(self):
        return self.title or f'Фото #{self.pk}'
    
    def get_image_size(self):
        """Возвращает размеры изображения"""
        try:
            if self.image:
                img = Image.open(self.image.path)
                return img.size
        except:
            pass
        return None
    
    def get_file_size_mb(self):
        """Возвращает размер файла в МБ"""
        try:
            if self.image:
                size_bytes = self.image.size
                return round(size_bytes / (1024 * 1024), 2)
        except:
            pass
        return None