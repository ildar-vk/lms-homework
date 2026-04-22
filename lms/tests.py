from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from users.models import User
from .models import Course, Lesson, Subscription


class LessonTests(APITestCase):
    def setUp(self):
        # Создаём пользователей
        self.user = User.objects.create_user(
            email='user@test.com',
            password='testpass123',
            first_name='Test'
        )
        self.moderator = User.objects.create_user(
            email='moderator@test.com',
            password='modpass123',
            first_name='Moderator'
        )
        self.other_user = User.objects.create_user(
            email='other@test.com',
            password='other123',
            first_name='Other'
        )
        
        # Назначаем модератора
        from django.contrib.auth.models import Group
        group, _ = Group.objects.get_or_create(name='moderators')
        self.moderator.groups.add(group)
        
        # Создаём курс
        self.course = Course.objects.create(
            title='Test Course',
            description='Test Description',
            owner=self.user
        )
        
        # Создаём урок
        self.lesson = Lesson.objects.create(
            title='Test Lesson',
            description='Lesson Description',
            course=self.course,
            owner=self.user,
            video_link='https://youtube.com/watch?v=123'
        )
        
        self.client = APIClient()
    
    def test_create_lesson_valid_youtube_link(self):
        """Тест: создание урока с валидной youtube ссылкой"""
        self.client.force_authenticate(user=self.user)
        url = reverse('lesson-list')
        data = {
            'title': 'New Lesson',
            'description': 'New Description',
            'course': self.course.id,
            'video_link': 'https://youtube.com/watch?v=abc123'
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
    
    def test_create_lesson_invalid_link(self):
        """Тест: создание урока с невалидной ссылкой (должно быть 400)"""
        self.client.force_authenticate(user=self.user)
        url = reverse('lesson-list')
        data = {
            'title': 'New Lesson',
            'description': 'New Description',
            'course': self.course.id,
            'video_link': 'https://rutube.ru/watch?v=123'
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_user_can_only_see_own_lessons(self):
        """Тест: пользователь видит только свои уроки"""
        self.client.force_authenticate(user=self.user)
        url = reverse('lesson-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Проверяем, что урок принадлежит пользователю
        self.assertEqual(response.data['results'][0]['owner'], self.user.id)
    
    def test_moderator_can_edit_any_lesson(self):
        """Тест: модератор может редактировать любой урок"""
        self.client.force_authenticate(user=self.moderator)
        url = reverse('lesson-detail', args=[self.lesson.id])
        data = {'title': 'Updated by Moderator'}
        response = self.client.patch(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.lesson.refresh_from_db()
        self.assertEqual(self.lesson.title, 'Updated by Moderator')
    
    def test_moderator_cannot_delete_lesson(self):
        """Тест: модератор не может удалять уроки"""
        self.client.force_authenticate(user=self.moderator)
        url = reverse('lesson-detail', args=[self.lesson.id])
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class SubscriptionTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email='user@test.com',
            password='testpass123'
        )
        self.course = Course.objects.create(
            title='Test Course',
            description='Test Description',
            owner=self.user
        )
        self.client = APIClient()
    
    def test_add_subscription(self):
        """Тест: добавление подписки"""
        self.client.force_authenticate(user=self.user)
        url = reverse('subscription')
        response = self.client.post(url, {'course_id': self.course.id}, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['message'], 'Подписка добавлена')
    
    def test_remove_subscription(self):
        """Тест: удаление подписки"""
        self.client.force_authenticate(user=self.user)
        url = reverse('subscription')
        # Добавляем подписку
        self.client.post(url, {'course_id': self.course.id}, format='json')
        # Удаляем подписку
        response = self.client.post(url, {'course_id': self.course.id}, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['message'], 'Подписка удалена')
    
    def test_subscription_requires_auth(self):
        """Тест: подписка требует авторизации"""
        url = reverse('subscription')
        response = self.client.post(url, {'course_id': self.course.id}, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
