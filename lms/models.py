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
