from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings
from django.utils import timezone
from datetime import timedelta
from users.models import User
from .models import Course, Subscription


@shared_task
def send_course_update_notification(course_id, updated_fields):
    """Отправка уведомлений подписчикам об обновлении курса"""
    try:
        course = Course.objects.get(id=course_id)
        subscriptions = Subscription.objects.filter(course=course)
        
        if not subscriptions.exists():
            return f"No subscribers for course {course.title}"
        
        # Формируем письмо
        subject = f"Курс '{course.title}' был обновлён!"
        message = f"""
        Здравствуйте!
        
        Курс '{course.title}' был обновлён.
        
        Обновлённые поля: {', '.join(updated_fields)}
        
        Ссылка на курс: http://localhost:8000/api/courses/{course_id}/
        
        С уважением,
        Команда LMS
        """
        
        recipients = [sub.user.email for sub in subscriptions]
        
        send_mail(
            subject=subject,
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=recipients,
            fail_silently=False,
        )
        
        return f"Notified {len(recipients)} subscribers about course '{course.title}'"
    
    except Course.DoesNotExist:
        return f"Course {course_id} not found"


@shared_task
def block_inactive_users():
    """Блокировка пользователей, не заходивших более месяца"""
    cutoff_date = timezone.now() - timedelta(days=30)
    
    # Находим неактивных пользователей
    inactive_users = User.objects.filter(
        last_login__lt=cutoff_date,
        is_active=True,
        is_superuser=False  # Не блокируем админов
    )
    
    count = inactive_users.count()
    
    # Блокируем
    inactive_users.update(is_active=False)
    
    return f"Blocked {count} inactive users (last login before {cutoff_date})"


@shared_task
def check_course_last_update(course_id):
    """Проверка, когда курс обновлялся в последний раз"""
    from .models import CourseUpdateLog
    
    try:
        last_update = CourseUpdateLog.objects.filter(course_id=course_id).latest('updated_at')
        now = timezone.now()
        hours_since_update = (now - last_update.updated_at).total_seconds() / 3600
        
        return {
            'course_id': course_id,
            'last_update': last_update.updated_at,
            'hours_since_update': hours_since_update,
            'can_notify': hours_since_update >= 4
        }
    except CourseUpdateLog.DoesNotExist:
        return {
            'course_id': course_id,
            'last_update': None,
            'hours_since_update': None,
            'can_notify': True
        }
