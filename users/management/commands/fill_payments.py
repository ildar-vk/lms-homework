from django.core.management.base import BaseCommand
from users.models import User, Payment
from lms.models import Course, Lesson
from decimal import Decimal


class Command(BaseCommand):
    help = 'Fill payments table with test data'
    
    def handle(self, *args, **options):
        user = User.objects.first()
        if not user:
            self.stdout.write(self.style.ERROR('No users found. Please create a user first.'))
            return
        
        course = Course.objects.first()
        lesson = Lesson.objects.first()
        
        # Очищаем старые платежи
        count_before = Payment.objects.count()
        Payment.objects.all().delete()
        self.stdout.write(f'Deleted {count_before} old payments')
        
        # Создаём новые платежи
        created_count = 0
        
        if course:
            Payment.objects.create(
                user=user,
                paid_course=course,
                amount=Decimal('4999.00'),
                payment_method='transfer'
            )
            created_count += 1
            self.stdout.write(f'✓ Created payment for course: {course.title}')
        
        if lesson:
            Payment.objects.create(
                user=user,
                paid_lesson=lesson,
                amount=Decimal('1999.00'),
                payment_method='cash'
            )
            created_count += 1
            self.stdout.write(f'✓ Created payment for lesson: {lesson.title}')
        
        # Создаём платеж без привязки к курсу/уроку
        Payment.objects.create(
            user=user,
            amount=Decimal('2999.00'),
            payment_method='transfer'
        )
        created_count += 1
        self.stdout.write('✓ Created generic payment')
        
        self.stdout.write(self.style.SUCCESS(f'✓ Total created {created_count} payments'))
