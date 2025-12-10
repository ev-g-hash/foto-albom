from django.apps import AppConfig
import os

class FotosConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'fotos'
    
    def ready(self):
        # Создаём папки для медиа файлов при старте
        from django.conf import settings
        media_dir = os.path.join(settings.MEDIA_ROOT, 'photos')
        print(f"🔍 MEDIA_ROOT = {settings.MEDIA_ROOT}")
        print(f"🔍 Creating photos folder at: {media_dir}")
        os.makedirs(media_dir, exist_ok=True)
        print(f"✅ Папка для фото создана: {media_dir}")
        
        # Также создаём папку для превью
        thumbs_dir = os.path.join(settings.MEDIA_ROOT, 'thumbnails')
        os.makedirs(thumbs_dir, exist_ok=True)
        print(f"✅ Папка для превью создана: {thumbs_dir}")
        
        # Создаём папку для временных файлов - ВАЖНО!
        temp_dir = os.path.join(settings.MEDIA_ROOT, 'temp_uploads')
        os.makedirs(temp_dir, exist_ok=True)
        print(f"✅ Папка для временных файлов создана: {temp_dir}")