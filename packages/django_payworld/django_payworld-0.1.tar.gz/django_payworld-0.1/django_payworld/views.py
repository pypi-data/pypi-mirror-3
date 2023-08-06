
from django.utils.translation import ugettext_lazy as _
from django.http import HttpResponse
from django.conf import settings

from django.views.generic.simple import direct_to_template
from django.views.decorators.csrf import csrf_exempt

from django_payworld.forms import PaymentForm
from django_payworld.signals import payment_notification, payment_error
from django_payworld.utils import calculate_hash


@csrf_exempt
def success(request):
    params_dict = {}
    if request.POST:
        for param in (
            'transaction_id',
            'order_id',
            'order_total',
            'result_message',
        ):
            params_dict[param] = request.POST.get(param, "")

        return direct_to_template(
                request,
                'django_payworld/success.html',
                params_dict,
        )
    return HttpResponse("POST Only")

@csrf_exempt
def failure(request):
    params_dict = {}
    if request.POST:
        for param in (
            'transaction_id',
            'order_id',
            'order_total',
            'result_message',
        ):
            params_dict[param] = request.POST.get(param, "")

        return direct_to_template(
                request,
                'django_payworld/failure.html',
                params_dict,
        )
    return HttpResponse("POST Only")

@csrf_exempt
def result(request):
    if request.POST:
        params_dict = {}
        for param in (
            'transaction_id',
            'order_id',
            'order_total',
            'payer_email',
            'seller_name',
            'shop_id',
            'hash',
        ):
            params_dict[param] = request.POST.get(param, "")
        if params_dict['hash'] == calculate_hash(
            params_dict,
            settings.PAYWORLD_SECRET_CODE
        ):
            del params_dict['hash']
            payment_notification.send(result, **params_dict)
        else:
            payment_error.send(result, **params_dict)

        return HttpResponse("OK")
    return HttpResponse("POST Only")

