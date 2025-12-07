from django.apps import AppConfig
import os

class FotosConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'fotos'
    
    def ready(self):
        # Создаём папки для медиа файлов при старте
        from django.conf import settings
        media_dir = os.path.join(settings.MEDIA_ROOT, 'photos')
        os.makedirs(media_dir, exist_ok=True)
        print(f"✅ Папка для фото создана: {media_dir}")