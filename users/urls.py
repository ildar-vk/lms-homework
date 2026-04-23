from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from .views import UserCreateAPIView, UserProfileAPIView, PaymentListAPIView
from .views_payment import CoursePaymentAPIView, PaymentStatusAPIView

urlpatterns = [
    path('register/', UserCreateAPIView.as_view(), name='user-register'),
    path('login/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('profile/', UserProfileAPIView.as_view(), name='user-profile'),
    path('payments/', PaymentListAPIView.as_view(), name='payment-list'),
    path('pay-course/<int:course_id>/', CoursePaymentAPIView.as_view(), name='pay-course'),
    path('payment-status/<int:payment_id>/', PaymentStatusAPIView.as_view(), name='payment-status'),
]
