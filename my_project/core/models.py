from django.db import models
from django.contrib.auth.models import AbstractUser
from django.conf import settings
from .constants import TOPIC_CHOICES

# --- ПОЛЬЗОВАТЕЛЬ ---
class User(AbstractUser):
    ROLE_CHOICES = (
        ('admin', 'Администратор'),
        ('blogger', 'Блогер'),
        ('advertiser', 'Рекламодатель'),
    )
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='blogger')
    email = models.EmailField(unique=True)

    def __str__(self):
        return f"{self.email} ({self.get_role_display()})"


# --- ПРОФИЛЬ БЛОГЕРА ---
class BloggerProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='blogger_profile')
    channel_name = models.CharField("Название канала", max_length=255)
    channel_link = models.URLField("Ссылка на канал")
    subscribers_count = models.PositiveIntegerField(default=0, verbose_name="Подписчиков")
    avatar_url = models.URLField(max_length=500, null=True, blank=True)
    banner_url = models.URLField(max_length=500, null=True, blank=True, verbose_name="Баннер канала")
    
    # Статистика
    median_views = models.PositiveIntegerField(default=0, verbose_name="Медиана просмотров (Long)")
    median_views_shorts = models.PositiveIntegerField(default=0, verbose_name="Медиана просмотров (Shorts)")

    # Прайс-лист
    price_start = models.DecimalField("Интеграция в начале", max_digits=10, decimal_places=2, default=0)
    price_middle = models.DecimalField("Интеграция в середине", max_digits=10, decimal_places=2, default=0)
    price_end = models.DecimalField("Интеграция в конце", max_digits=10, decimal_places=2, default=0)
    price_shorts = models.DecimalField("Цена за Shorts", max_digits=10, decimal_places=2, default=0)
    
    categories = models.CharField("Тематики", max_length=500) 
    description = models.TextField("Описание канала", blank=True)

    # Логика сокращения категорий (для карточки)
    def get_short_categories(self):
        if not self.categories:
            return "Без категории"
        choices_dict = dict(TOPIC_CHOICES)
        # Очищаем от подкатегорий после '|' и разбиваем
        main_part = self.categories.split('|')[0]
        cats = [choices_dict.get(c.strip(), c.strip()) for c in main_part.split(',') if c.strip()]
        if len(cats) > 2:
            return f"{cats[0]}, {cats[1]} и др."
        return ", ".join(cats)

    # Полный перевод для детальной страницы
    def get_categories_russian(self):
        if not self.categories:
            return ""
        choices_dict = dict(TOPIC_CHOICES)
        raw_list = [c.strip() for c in self.categories.split(',')]
        russian_list = [choices_dict.get(c, c) for c in raw_list]
        return ", ".join(russian_list)

    @property
    def price_long_min(self):
        prices = [self.price_start, self.price_middle, self.price_end]
        valid_prices = [p for p in prices if p > 0]
        return min(valid_prices) if valid_prices else 0

    @property
    def cpv_long(self):
        if self.median_views > 0 and self.price_long_min > 0:
            return round(float(self.price_long_min) / self.median_views, 2)
        return 0

    @property
    def cpv_shorts(self):
        if self.median_views_shorts > 0 and self.price_shorts > 0:
            return round(float(self.price_shorts) / self.median_views_shorts, 2)
        return 0

    def __str__(self):
        return f"Блогер: {self.channel_name} (@{self.user.username})"


# --- ПРОФИЛЬ РЕКЛАМОДАТЕЛЯ ---
class AdvertiserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='advertiser_profile')
    company_name = models.CharField("Название компании", max_length=255)

    def __str__(self):
        return self.company_name


# --- ОБЪЯВЛЕНИЕ ТОВАРА (Маркетплейс) ---
class ProductAd(models.Model):
    advertiser = models.ForeignKey(AdvertiserProfile, on_delete=models.CASCADE, related_name='ads')
    title = models.CharField("Название", max_length=200)
    description = models.TextField("Описание и ТЗ")
    category = models.CharField("Категории (через запятую)", max_length=500)
    
    # Изображения
    image = models.ImageField("Файл фото", upload_to='products/%Y/%m/%d/', blank=True, null=True)
    image_url = models.URLField("Ссылка на фото", blank=True, null=True, max_length=500)
    
    # Ссылки
    link_wb = models.URLField("Wildberries", max_length=500, null=True, blank=True)
    link_ozon = models.URLField("Ozon", max_length=500, null=True, blank=True)
    link_site = models.URLField("Сайт/Другое", max_length=500, null=True, blank=True)
    
    budget = models.DecimalField("Бюджет/Цена", max_digits=10, decimal_places=2, default=0)
    is_active = models.BooleanField("Опубликовать", default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Объявление товара"
        verbose_name_plural = "Объявления товаров"
        ordering = ['-created_at']

    def get_short_categories(self):
        if not self.category:
            return "Без категории"
        choices_dict = dict(TOPIC_CHOICES)
        cats = [choices_dict.get(c.strip(), c.strip()) for c in self.category.split(',') if c.strip()]
        if len(cats) > 2:
            return f"{cats[0]}, {cats[1]} и др."
        return ", ".join(cats)

    def __str__(self):
        return f"{self.title} ({self.advertiser.company_name})"


# --- ЧАТЫ ---
class Message(models.Model):
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_messages')
    receiver = models.ForeignKey(User, on_delete=models.CASCADE, related_name='received_messages')
    ad = models.ForeignKey(ProductAd, on_delete=models.SET_NULL, null=True, blank=True)
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

    class Meta:
        ordering = ['created_at']

    def __str__(self):
        return f"От {self.sender} к {self.receiver}"


# --- КОНТРАКТЫ ---
class AdContract(models.Model):
    STATUS_CHOICES = [
        ('created', 'Создан'),
        ('paid', 'Оплачен (Заморожено)'),
        ('completed', 'Завершен'),
        ('cancelled', 'Отменен'),
    ]
    
    number = models.CharField("Номер договора", max_length=50, unique=True)
    advertiser = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='adv_contracts')
    blogger = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='blogger_contracts')
    total_amount = models.DecimalField("Сумма", max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='created')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Договор"
        verbose_name_plural = "Договоры"

    def __str__(self):
        return f"Договор {self.number}"


# --- ЭТАПЫ (РОЛИКИ) ---
class VideoItem(models.Model):
    VIDEO_STATUS = [
        ('in_progress', 'В работе'),
        ('review', 'На утверждении'),
        ('correction', 'На доработке'),
        ('approved', 'Утвержден'),
        ('released', 'Выпущен'),
    ]
    
    contract = models.ForeignKey(AdContract, on_delete=models.CASCADE, related_name='videos')
    format = models.CharField("Формат", max_length=50)
    deadline = models.DateField("Дедлайн")
    status = models.CharField(max_length=20, choices=VIDEO_STATUS, default='in_progress')
    
    video_link = models.URLField("Ссылка на видео", blank=True, null=True)
    time_start = models.CharField("Начало рекламы", max_length=10, blank=True)
    time_end = models.CharField("Конец рекламы", max_length=10, blank=True)

    class Meta:
        verbose_name = "Ролик"
        verbose_name_plural = "Ролики"

    def __str__(self):
        return f"{self.format} для {self.contract.number}"


# --- ПОДДЕРЖКА ---
class SupportTicket(models.Model):
    email = models.EmailField()
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_resolved = models.BooleanField(default=False)

    def __str__(self):
        return f"От {self.email} - {self.created_at.strftime('%d.%m %H:%M')}"