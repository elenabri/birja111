import requests
import statistics
import re

def parse_duration_to_seconds(duration):
    """Разбирает формат ISO 8601 (PT1M30S) без сторонних библиотек"""
    hours = re.search(r'(\d+)H', duration)
    minutes = re.search(r'(\d+)M', duration)
    seconds = re.search(r'(\d+)S', duration)
    
    total_seconds = 0
    if hours: total_seconds += int(hours.group(1)) * 3600
    if minutes: total_seconds += int(minutes.group(1)) * 60
    if seconds: total_seconds += int(seconds.group(1))
    return total_seconds

def get_youtube_stats(channel_url, api_key):
    handle_match = re.search(r'@([\w\.-]+)', channel_url)
    if not handle_match: return None
    handle = handle_match.group(1)

    try:
        # 1. Получаем ID канала и ID плейлиста загрузок (Дешево: 1 единица)
        # Добавили contentDetails в part, чтобы узнать ID плейлиста всех видео
        ch_url = f"https://www.googleapis.com/youtube/v3/channels?part=snippet,statistics,contentDetails&forHandle={handle}&key={api_key}"
        ch_data = requests.get(ch_url, timeout=7).json()
        if not ch_data.get("items"): return None
        
        item = ch_data["items"][0]
        channel_name = item["snippet"]["title"]
        total_subs = int(item["statistics"].get("subscriberCount", 0))
        # ID плейлиста, где лежат ВСЕ загрузки канала
        uploads_id = item["contentDetails"]["relatedPlaylists"]["uploads"]

        # 2. Получаем последние 50 видео через плейлист (Дешево: 1 единица вместо 100!)
        pl_url = f"https://www.googleapis.com/youtube/v3/playlistItems?part=contentDetails&playlistId={uploads_id}&maxResults=50&key={api_key}"
        pl_data = requests.get(pl_url, timeout=7).json()
        video_ids = [v["contentDetails"]["videoId"] for v in pl_data.get("items", [])]

        if not video_ids:
            return {'name': channel_name, 'subs': total_subs, 'long_median': 0, 'shorts_median': 0}

        # 3. Получаем данные всех видео одним пакетом (Дешево: 1 единица)
        v_url = f"https://www.googleapis.com/youtube/v3/videos?part=contentDetails,statistics&id={','.join(video_ids)}&key={api_key}"
        v_data = requests.get(v_url, timeout=7).json()

        long_views = []
        shorts_views = []

        for v in v_data.get("items", []):
            views = int(v["statistics"].get("viewCount", 0))
            duration_sec = parse_duration_to_seconds(v["contentDetails"]["duration"])

            # Распределяем: Shorts < 2 мин, Long >= 2 мин (лимит по 5 для медианы)
            if duration_sec < 120:
                if len(shorts_views) < 5: shorts_views.append(views)
            else:
                if len(long_views) < 5: long_views.append(views)

        def safe_median(data_list):
            if not data_list: return 0
            return int(statistics.median(data_list))

        return {
            'name': channel_name,
            'subs': total_subs,
            'long_median': safe_median(long_views),
            'shorts_median': safe_median(shorts_views)
        }

    except Exception as e:
        print(f"Критическая ошибка YouTube API: {e}")
        return None