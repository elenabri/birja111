from django.contrib import admin
from .models import User, BloggerProfile, AdvertiserProfile, ProductAd, Message

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('username', 'email', 'role', 'is_staff')
    list_filter = ('role',)
    search_fields = ('username', 'email')

@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ('sender', 'receiver', 'created_at', 'is_read') 
    list_filter = ('created_at', 'is_read') # И здесь тоже
    search_fields = ('text', 'sender__username', 'receiver__username')

# Регистрируем остальные модели
admin.site.register(BloggerProfile)
admin.site.register(AdvertiserProfile)
admin.site.register(ProductAd)


from django.contrib import admin
from .models import SupportTicket

@admin.register(SupportTicket)
class SupportTicketAdmin(admin.ModelAdmin):
    list_display = ('email', 'created_at', 'is_resolved')
    list_filter = ('is_resolved', 'created_at')