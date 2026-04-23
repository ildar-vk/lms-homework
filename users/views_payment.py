from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from django.shortcuts import get_object_or_404
from lms.models import Course
from .models import Payment
from .services import create_stripe_product, create_stripe_price, create_stripe_checkout_session


class CoursePaymentAPIView(APIView):
    """Создание оплаты для курса через Stripe"""
    permission_classes = [IsAuthenticated]
    
    def post(self, request, course_id):
        user = request.user
        course = get_object_or_404(Course, id=course_id)
        
        # Цена курса (можно добавить поле price в модель Course)
        amount = 4999.00
        
        # 1. Создаём продукт в Stripe
        product = create_stripe_product(course.title, course.description)
        if not product:
            return Response(
                {'error': 'Failed to create Stripe product'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        
        # 2. Создаём цену в Stripe
        price = create_stripe_price(amount, product.id)
        if not price:
            return Response(
                {'error': 'Failed to create Stripe price'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        
        # 3. Создаём сессию для оплаты
        session = create_stripe_checkout_session(price.id)
        if not session:
            return Response(
                {'error': 'Failed to create Stripe session'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        
        # 4. Сохраняем платёж в БД
        payment = Payment.objects.create(
            user=user,
            paid_course=course,
            amount=amount,
            payment_method='transfer',
            stripe_session_id=session.id,
            stripe_payment_url=session.url,
            status='pending'
        )
        
        return Response({
            'payment_id': payment.id,
            'amount': amount,
            'payment_url': session.url,
            'session_id': session.id
        }, status=status.HTTP_201_CREATED)


class PaymentStatusAPIView(APIView):
    """Проверка статуса платежа"""
    permission_classes = [IsAuthenticated]
    
    def get(self, request, payment_id):
        payment = get_object_or_404(Payment, id=payment_id, user=request.user)
        
        return Response({
            'payment_id': payment.id,
            'amount': payment.amount,
            'status': payment.status,
            'payment_url': payment.stripe_payment_url,
            'created_at': payment.payment_date
        })
