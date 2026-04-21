from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views
from django.conf import settings
from django.conf.urls.static import static
from core import views  

# Группируем все маршруты основного приложения с именем 'core'
core_patterns = ([
    path('', views.home, name='home'),
    path('register/', views.register, name='register'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('marketplace/', views.marketplace, name='marketplace'),
    
    # API и AJAX
    path('api/fetch-youtube/', views.fetch_youtube_data, name='fetch_youtube'),
    path('ajax/check-email/', views.check_email, name='check_email'),
    path('support-ajax/', views.support_ajax, name='support_ajax'),
    path('activate/<uidb64>/<token>/', views.activate, name='activate'),

    # Чаты и взаимодействие
    path('chats/', views.chat_list, name='chat_list'),
    path('chats/<int:chat_id>/', views.chat_detail, name='chat_detail'),
    path('send_response/<int:ad_id>/', views.send_response, name='send_response'),
    path('bulk-message-setup/', views.bulk_message_setup, name='bulk_message_setup'),
    
    # Кабинеты и профили
    path('my-products/', views.manage_products, name='manage_products'),
    path('my-products/delete/<int:pk>/', views.delete_product, name='delete_product'),
    path('blogger/profile/', views.edit_blogger_profile, name='edit_blogger_profile'),
    path('product/<int:pk>/', views.product_detail, name='product_detail'),
    path('seller/<int:pk>/', views.seller_profile, name='seller_profile'),
    path('integration/', views.integration, name='integration'),
    
    # Роутер
    path('login-router/', views.login_router, name='login_router'),
], 'core')

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # Подключаем наши основные пути через include с namespace
    path('', include(core_patterns)),

    # Встроенная авторизация (login/logout)
    path('accounts/', include('django.contrib.auth.urls')),

    # Сброс пароля (auth_views)
    path('password-reset/', auth_views.PasswordResetView.as_view(
        template_name='registration/password_reset_form.html',
        email_template_name='registration/password_reset_email.html',
        subject_template_name='registration/password_reset_subject.txt',
    ), name='password_reset'),
    
    path('password-reset/done/', auth_views.PasswordResetDoneView.as_view(
        template_name='registration/password_reset_done.html'
    ), name='password_reset_done'),
    
    path('password-reset-confirm/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(
        template_name='registration/password_reset_confirm.html'
    ), name='password_reset_confirm'),
    
    path('password-reset-complete/', auth_views.PasswordResetCompleteView.as_view(
        template_name='registration/password_reset_complete.html'
    ), name='password_reset_complete'),

]

# Подключаем статику и медиафайлы
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)