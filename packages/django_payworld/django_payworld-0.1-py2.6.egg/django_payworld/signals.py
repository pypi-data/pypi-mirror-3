import django.dispatch

payment_notification = django.dispatch.Signal(providing_args=[
    "transaction_id",
    "order_id",
    "order_total",
    "payer_email",
    "seller_name",
    "shop_id",
])

payment_error = django.dispatch.Signal(providing_args=[
    "transaction_id",
    "order_id",
    "order_total",
    "payer_email",
    "seller_name",
    "shop_id",
    "hash",
])
