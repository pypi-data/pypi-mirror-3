from django.conf import settings

def get(key, default):
     return getattr(settings, key, default)

TEST_PAYMENT_URL = get('PAYWORLD_TEST_PAYMENT_URL',
    'https://pay-world.ru/paymentsystem/enter-test/')
REAL_PAYMENT_URL = get('PAYWORLD_REAL_PAYMENT_URL',
    'https://pay-world.ru/paymentsystem/enter/')
TEST_MODE = get('PAYWORLD_TEST_MODE', True)

if TEST_MODE:
    PAYMENT_URL = REAL_PAYMENT_URL
else:
    PAYMENT_URL = TEST_PAYMENT_URL
