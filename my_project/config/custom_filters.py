from django import template

register = template.Library()

@register.filter
def split_tags(value):
    """
    Превращает строку вида 'Категория 1, Категория 2 | Тег 1, Тег 2'
    в чистый список ['Категория 1', 'Категория 2', 'Тег 1', 'Тег 2'].
    """
    if not value:
        return []
    
    # 1. Заменяем разделитель блоков "|" на запятую
    # Теперь у нас строка только с запятыми
    unified_string = value.replace('|', ',')
    
    # 2. Разбиваем строку по запятой
    parts = unified_string.split(',')
    
    # 3. Очищаем каждый элемент от лишних пробелов по краям
    # и убираем пустые элементы, если они возникли (например, лишняя запятая)
    clean_list = [item.strip() for item in parts if item.strip()]
    
    return clean_list