from django.db import models
from users.models import User

class Course(models.Model):
    title = models.CharField(max_length=200)
    preview = models.ImageField(upload_to='course_previews/', blank=True, null=True)
    description = models.TextField()

    owner = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, related_name='courses')

    def __str__(self):
        return self.title

class Lesson(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    preview = models.ImageField(upload_to='lesson_previews/', blank=True, null=True)
    video_link = models.URLField(blank=True, null=True)
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='lessons')

    owner = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, related_name='lessons')

    def __str__(self):
        return self.title


class Subscription(models.Model):
    user = models.ForeignKey('users.User', on_delete=models.CASCADE, related_name='subscriptions')
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='subscriptions')
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ('user', 'course')
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'
    
    def __str__(self):
        return f'{self.user.email} -> {self.course.title}'


class CourseUpdateLog(models.Model):
    """Лог обновлений курса для отслеживания времени последнего обновления"""
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='update_logs')
    updated_at = models.DateTimeField(auto_now_add=True)
    updated_fields = models.JSONField(default=list)
    
    class Meta:
        ordering = ['-updated_at']
        verbose_name = 'Лог обновления курса'
        verbose_name_plural = 'Логи обновлений курсов'
    
    def __str__(self):
        return f"{self.course.title} - {self.updated_at}"
