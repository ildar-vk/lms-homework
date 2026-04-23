from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Course, CourseUpdateLog
from .tasks import send_course_update_notification
from django.utils import timezone


@receiver(post_save, sender=Course)
def send_course_update_notification_signal(sender, instance, created, **kwargs):
    """Отправляет уведомления при обновлении курса"""
    
    if created:
        return  # Не отправляем для новых курсов
    
    # Получаем последний лог обновления
    last_log = CourseUpdateLog.objects.filter(course=instance).first()
    
    # Проверяем, было ли обновление более 4 часов назад
    if last_log:
        hours_since = (timezone.now() - last_log.updated_at).total_seconds() / 3600
        if hours_since < 4:
            print(f"DEBUG: Skipping notification for course {instance.id} - last update was {hours_since:.1f} hours ago")
            return
    
    # Отправляем уведомление
    print(f"DEBUG: Sending notification for course {instance.id}")
    send_course_update_notification.delay(instance.id, ['content'])
    
    # Создаём лог обновления
    CourseUpdateLog.objects.create(
        course=instance,
        updated_fields=['content']
    )
