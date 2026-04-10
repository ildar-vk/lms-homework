from rest_framework import serializers
from .models import User, Payment


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'email', 'first_name', 'last_name', 'phone', 'city', 'avatar', 'password']
        extra_kwargs = {'password': {'write_only': True}}
    
    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        return user


class PaymentSerializer(serializers.ModelSerializer):
    user_email = serializers.CharField(source='user.email', read_only=True)
    course_title = serializers.CharField(source='paid_course.title', read_only=True, default=None)
    lesson_title = serializers.CharField(source='paid_lesson.title', read_only=True, default=None)
    
    class Meta:
        model = Payment
        fields = ['id', 'user', 'user_email', 'payment_date', 'paid_course', 'course_title', 
                  'paid_lesson', 'lesson_title', 'amount', 'payment_method']


class UserProfileSerializer(serializers.ModelSerializer):
    payments = PaymentSerializer(many=True, read_only=True)
    
    class Meta:
        model = User
        fields = ['id', 'email', 'phone', 'city', 'avatar', 'first_name', 'last_name', 'payments']
        read_only_fields = ['id', 'email', 'payments']


class PublicUserSerializer(serializers.ModelSerializer):
    """Публичный профиль пользователя (без чувствительных данных)"""
    class Meta:
        model = User
        fields = ['id', 'email', 'first_name', 'city', 'avatar']
