from django.db import models
import os
import uuid  
from PIL import Image
from django.core.exceptions import ValidationError
from django.conf import settings

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
    
    # Возвращаем путь с оптимизированным именем - относительно MEDIA_ROOT
    return os.path.join('photos', f"{filename_base}.jpg")

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
    thumbnail = models.ImageField('Превью', upload_to='thumbnails', blank=True, null=True)

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
    
    def delete(self, *args, **kwargs):
        """Переопределяем delete для удаления файлов с диска"""
        try:
            # Удаляем основное изображение
            if self.image and self.image.name:
                # Получаем полный путь к файлу
                if hasattr(self.image, 'path'):
                    file_path = self.image.path
                    # Удаляем файл если он существует
                    if os.path.exists(file_path):
                        os.remove(file_path)
                        print(f"🗑️ Удалён файл: {file_path}")
        except Exception as e:
            print(f"⚠️ Ошибка при удалении основного файла: {e}")
        
        try:
            # Удаляем превью если есть
            if self.thumbnail and self.thumbnail.name:
                if hasattr(self.thumbnail, 'path'):
                    thumb_path = self.thumbnail.path
                    if os.path.exists(thumb_path):
                        os.remove(thumb_path)
                        print(f"🗑️ Удалён превью файл: {thumb_path}")
        except Exception as e:
            print(f"⚠️ Ошибка при удалении превью файла: {e}")
        
        # Удаляем запись из базы данных
        super().delete(*args, **kwargs)
    
    def save(self, *args, **kwargs):
        """Переопределяем save для удаления старого файла при замене"""
        # Проверяем, обновляется ли существующий объект
        if self.pk:
            try:
                old_photo = Photo.objects.get(pk=self.pk)
                # Если файл изменился, удаляем старый
                if old_photo.image.name != self.image.name:
                    if old_photo.image and old_photo.image.name:
                        if hasattr(old_photo.image, 'path'):
                            old_file_path = old_photo.image.path
                            if os.path.exists(old_file_path):
                                os.remove(old_file_path)
                                print(f"🗑️ Заменён старый файл: {old_file_path}")
                
                # Если превью изменилось, удаляем старое превью
                if old_photo.thumbnail and self.thumbnail:
                    if old_photo.thumbnail.name != self.thumbnail.name:
                        if old_photo.thumbnail.name:
                            if hasattr(old_photo.thumbnail, 'path'):
                                old_thumb_path = old_photo.thumbnail.path
                                if os.path.exists(old_thumb_path):
                                    os.remove(old_thumb_path)
                                    print(f"🗑️ Заменено старое превью: {old_thumb_path}")
            except Photo.DoesNotExist:
                pass  # Новый объект
        
        super().save(*args, **kwargs)