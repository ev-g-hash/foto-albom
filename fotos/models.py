from django.db import models
import os
import uuid

def photo_upload_path(instance, filename):
    """Генерирует путь для сохранения файла с оригинальным именем"""
    # Получаем расширение файла
    ext = filename.split('.')[-1]
    # Если у объекта есть ID, используем его, иначе генерируем временный
    if instance.pk:
        filename_base = str(instance.pk)
    else:
        # Для новых объектов используем временное имя
        filename_base = f"temp_{uuid.uuid4().hex[:8]}"
    
    # Возвращаем путь с оригинальным именем файла
    # Используем относительный путь от MEDIA_ROOT
    return os.path.join('photos/', filename)

class Photo(models.Model):
    title = models.CharField('Название', max_length=200, blank=True)
    description = models.TextField('Описание', blank=True)
    image = models.ImageField('Изображение', upload_to=photo_upload_path)
    created_at = models.DateTimeField('Дата создания', auto_now_add=True)

    class Meta:
        ordering = ['id'] 
        verbose_name = 'Фото'
        verbose_name_plural = 'Фотографии'

    def __str__(self):
        return self.title or f'Фото #{self.pk}'