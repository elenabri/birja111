import os
import django
import requests
import time

# 1. Настройка окружения
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from core.models import BloggerProfile
from core.views import get_youtube_stats, YOUTUBE_API_KEY

def update_all_banners():
    # Берем всех блогеров
    bloggers = BloggerProfile.objects.all()
    print(f"--- Запуск обновления. Найдено профилей: {bloggers.count()} ---")

    for blogger in bloggers:
        print(f"\nОбработка: {blogger.channel_name}")
        print(f"URL в базе: {blogger.channel_link}")

        if not blogger.channel_link:
            print("Результат: Ссылка отсутствует в БД.")
            continue

        try:
            # Вызываем функцию
            stats = get_youtube_stats(blogger.channel_link, YOUTUBE_API_KEY)
            
            if stats:
                print(f"Данные получены: {stats.get('name')}")
                print(f"Аватар: {'OK' if stats.get('avatar') else 'НЕТ'}")
                print(f"Баннер: {'OK' if stats.get('banner') else 'НЕТ (у канала может не быть баннера)'}")
                
                # Обновляем поля
                blogger.avatar_url = stats.get('avatar')
                blogger.banner_url = stats.get('banner')
                blogger.save()
                print("Результат: Профиль успешно обновлен в БД.")
            else:
                print("Результат: Функция get_youtube_stats вернула None (канал не найден или ошибка API).")
        
        except Exception as e:
            print(f"Результат: Критическая ошибка при обработке: {e}")

        time.sleep(1) # Задержка 1 секунда

if __name__ == '__main__':
    update_all_banners()