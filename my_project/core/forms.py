from django import forms
from .models import User
from django.contrib.auth.forms import AuthenticationForm
from .constants import TOPIC_CHOICES

class RegistrationForm(forms.ModelForm):
    # Поле username скрываем, чтобы оно не мешалось в интерфейсе
    username = forms.CharField(widget=forms.HiddenInput(), required=False)
    
    role = forms.ChoiceField(
        choices=[('blogger', 'Блогер'), ('advertiser', 'Рекламодатель')], 
        label="Кто вы?"
    )
    
    # Поля блогера (Название канала удалено)
    channel_link = forms.CharField( # Меняем на CharField, чтобы убрать браузерную проверку URL
    required=False, 
    label="Ссылка на канал",
    widget=forms.TextInput(attrs={
        'placeholder': 'https://www.youtube.com/@yourchannel',
        'class': 'form-control'
    })
)
    
    price_start = forms.DecimalField(required=False, label="Начало")
    price_middle = forms.DecimalField(required=False, label="Середина")
    price_end = forms.DecimalField(required=False, label="Конец")
    price_shorts = forms.DecimalField(required=False, label="Shorts")
    
    topics = forms.MultipleChoiceField(
        choices=TOPIC_CHOICES, 
        widget=forms.CheckboxSelectMultiple, 
        required=False,
        label="Тематики"
    )

    # Поля рекламодателя
    company_name = forms.CharField(required=False, label="Название компании")
    product_title = forms.CharField(required=False, label="Название товара")
    product_link = forms.URLField(required=False, label="Ссылка на продукт")

    class Meta:
        model = User
        fields = ['username', 'email']

class EmailLoginForm(AuthenticationForm):
    username = forms.EmailField(
        label="Почта", 
        widget=forms.EmailInput(attrs={
            'placeholder': 'example@mail.com',
            'class': 'form-control'
        })
    )
    password = forms.CharField(
        label="Пароль", 
        widget=forms.PasswordInput(attrs={
            'placeholder': '********',
            'class': 'form-control'
        })
    )