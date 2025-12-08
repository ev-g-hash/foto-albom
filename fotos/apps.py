from django.apps import AppConfig
import os

class FotosConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'fotos'
    
    def ready(self):
        from django.conf import settings
        
        # Создаём папки для медиа файлов при старте
        media_dir = os.path.join(settings.MEDIA_ROOT, 'photos')
        try:
            os.makedirs(media_dir, exist_ok=True)
            print(f"✅ Папка для фото создана: {media_dir}")
        except Exception as e:
            print(f"❌ Ошибка создания папки: {e}")