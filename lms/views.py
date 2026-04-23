from rest_framework import viewsets, generics
from rest_framework.permissions import IsAuthenticated
from .models import Course, Lesson, CourseUpdateLog
from .serializers import CourseSerializer, LessonSerializer
from django.utils import timezone
from .tasks import send_course_update_notification
from .paginators import CoursePaginator, LessonPaginator
from users.permissions import IsModerator, IsOwner


class CourseViewSet(viewsets.ModelViewSet):
    queryset = Course.objects.all()  # Добавляем queryset
    serializer_class = CourseSerializer
    pagination_class = CoursePaginator

    def get_queryset(self):
        user = self.request.user
        if IsModerator().has_permission(self.request, self):
            return Course.objects.all()
        return Course.objects.filter(owner=user)

    def get_permissions(self):
        if self.action == 'create':
            self.permission_classes = [IsAuthenticated, ~IsModerator]
        elif self.action == 'destroy':
            self.permission_classes = [IsAuthenticated, ~IsModerator, IsOwner]
        elif self.action in ['update', 'partial_update']:
            self.permission_classes = [IsAuthenticated, IsModerator | IsOwner]
        else:
            self.permission_classes = [IsAuthenticated]
        return [permission() for permission in self.permission_classes]

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)


class LessonListCreateView(generics.ListCreateAPIView):
    queryset = Lesson.objects.all()  # Добавляем queryset
    serializer_class = LessonSerializer
    pagination_class = LessonPaginator

    def get_queryset(self):
        user = self.request.user
        if IsModerator().has_permission(self.request, self):
            return Lesson.objects.all()
        return Lesson.objects.filter(owner=user)

    def get_permissions(self):
        if self.request.method == 'POST':
            self.permission_classes = [IsAuthenticated, ~IsModerator]
        else:
            self.permission_classes = [IsAuthenticated]
        return [permission() for permission in self.permission_classes]

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)


class LessonRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Lesson.objects.all()  # Добавляем queryset
    serializer_class = LessonSerializer

    def get_queryset(self):
        user = self.request.user
        if IsModerator().has_permission(self.request, self):
            return Lesson.objects.all()
        return Lesson.objects.filter(owner=user)

    def get_permissions(self):
        if self.request.method == 'DELETE':
            self.permission_classes = [IsAuthenticated, ~IsModerator, IsOwner]
        elif self.request.method in ['PUT', 'PATCH']:
            self.permission_classes = [IsAuthenticated, IsModerator | IsOwner]
        else:
            self.permission_classes = [IsAuthenticated]
        return [permission() for permission in self.permission_classes]
    def perform_update(self, serializer):
        course = self.get_object()
        old_data = {
            'title': course.title,
            'description': course.description,
        }
        
        # Сохраняем обновление
        serializer.save()
        
        # Определяем, какие поля были изменены
        updated_fields = []
        if old_data['title'] != serializer.instance.title:
            updated_fields.append('title')
        if old_data['description'] != serializer.instance.description:
            updated_fields.append('description')
        
        if updated_fields:
            # Проверяем, когда было последнее обновление
            last_update_log = CourseUpdateLog.objects.filter(course=course).first()
            
            # Если не обновляли более 4 часов или нет лога — отправляем уведомление
            if not last_update_log or (timezone.now() - last_update_log.updated_at).total_seconds() > 4 * 3600:
                # Отправляем уведомление подписчикам
                send_course_update_notification.delay(course.id, updated_fields)
            
            # Логируем обновление
            CourseUpdateLog.objects.create(
                course=course,
                updated_fields=updated_fields
            )
