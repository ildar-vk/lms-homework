from django.contrib import admin
from .models import User, Payment

admin.site.register(User)


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ['user', 'amount', 'payment_method', 'payment_date', 'paid_course', 'paid_lesson']
    list_filter = ['payment_method', 'payment_date']
    search_fields = ['user__email']
