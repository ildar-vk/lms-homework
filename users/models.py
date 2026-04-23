from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models


class UserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("Email must be set")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_active", True)
        
        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")
            
        return self.create_user(email, password, **extra_fields)


class User(AbstractUser):
    username = None
    email = models.EmailField(unique=True, verbose_name="Электронная почта")
    phone = models.CharField(max_length=35, blank=True, null=True, verbose_name="Телефон")
    city = models.CharField(max_length=100, blank=True, null=True, verbose_name="Город")
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True, verbose_name="Аватар")
    
    objects = UserManager()
    
    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []
    
    class Meta:
        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"
    
    def __str__(self):
        return self.email


class Payment(models.Model):
    PAYMENT_METHODS = (
        ('cash', 'Наличные'),
        ('transfer', 'Перевод на счет'),
    )
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='payments', verbose_name="Пользователь")
    payment_date = models.DateTimeField(auto_now_add=True, verbose_name="Дата оплаты")
    paid_course = models.ForeignKey('lms.Course', on_delete=models.SET_NULL, null=True, blank=True, related_name='payments', verbose_name="Оплаченный курс")
    paid_lesson = models.ForeignKey('lms.Lesson', on_delete=models.SET_NULL, null=True, blank=True, related_name='payments', verbose_name="Оплаченный урок")
    amount = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Сумма оплаты")
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHODS, verbose_name="Способ оплаты")
    
    class Meta:
        verbose_name = "Платеж"
        verbose_name_plural = "Платежи"
        ordering = ['-payment_date']
    
    def __str__(self):
        return f"{self.user.email} - {self.amount} - {self.payment_date}"

    # Добавить в модель Payment эти поля:
    stripe_session_id = models.CharField(max_length=255, blank=True, null=True, verbose_name="ID сессии Stripe")
    stripe_payment_url = models.URLField(blank=True, null=True, verbose_name="Ссылка на оплату Stripe")
    status = models.CharField(
        max_length=50, 
        default='pending', 
        choices=[
            ('pending', 'Ожидает оплаты'),
            ('paid', 'Оплачен'),
            ('failed', 'Ошибка'),
            ('cancelled', 'Отменён'),
        ],
        verbose_name="Статус платежа"
    )
