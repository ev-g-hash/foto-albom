from django.apps import AppConfig
import os

class FotosConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'fotos'
    
    def ready(self):
        from django.conf import settings
        from django.core.files.storage import default_storage
        
        # Проверяем статические файлы
        print(f"🔍 STATIC_ROOT = {settings.STATIC_ROOT}")
        print(f"🔍 STATIC_URL = {settings.STATIC_URL}")
        print(f"🔍 STATICFILES_DIRS = {settings.STATICFILES_DIRS}")
        
        # Проверяем что файлы существуют
        css_path = os.path.join(settings.STATIC_ROOT, 'fotos/css/style.css')
        js_path = os.path.join(settings.STATIC_ROOT, 'fotos/js/main.js')
        print(f"🔍 CSS exists: {os.path.exists(css_path)}")
        print(f"🔍 JS exists: {os.path.exists(js_path)}")
        
        # Создаём папки для медиа файлов
        media_dir = os.path.join(settings.MEDIA_ROOT, 'photos')
        os.makedirs(media_dir, exist_ok=True)
        print(f"✅ Папка для фото создана: {media_dir}")