import stripe
from django.conf import settings

# Настройка Stripe
stripe.api_key = settings.STRIPE_SECRET_KEY


def create_stripe_product(name, description=None):
    """Создание продукта в Stripe"""
    try:
        product = stripe.Product.create(
            name=name,
            description=description or f"Курс: {name}",
        )
        print(f"✅ Product created: {product.id}")
        return product
    except stripe.error.StripeError as e:
        print(f"❌ Stripe error creating product: {e}")
        return None


def create_stripe_price(amount, product_id, currency='rub'):
    """Создание цены в Stripe (сумма в копейках!)"""
    try:
        price = stripe.Price.create(
            product=product_id,
            unit_amount=int(amount * 100),  # рубли → копейки
            currency=currency,
        )
        print(f"✅ Price created: {price.id}")
        return price
    except stripe.error.StripeError as e:
        print(f"❌ Stripe error creating price: {e}")
        return None


def create_stripe_checkout_session(price_id, success_url='http://localhost:8000/success', cancel_url='http://localhost:8000/cancel'):
    """Создание сессии для оплаты"""
    try:
        session = stripe.checkout.Session.create(
            success_url=success_url,
            cancel_url=cancel_url,
            line_items=[
                {
                    'price': price_id,
                    'quantity': 1,
                },
            ],
            mode='payment',
        )
        print(f"✅ Checkout session created: {session.id}")
        print(f"   Payment URL: {session.url}")
        return session
    except stripe.error.StripeError as e:
        print(f"❌ Stripe error creating session: {e}")
        return None
