from django import forms
from django.utils.translation import ugettext_lazy as _

from django.conf import settings

class PaymentForm(forms.Form):
    order_id = forms.CharField(widget=forms.HiddenInput())
    order_total = forms.DecimalField(widget=forms.HiddenInput())
    order_details = forms.CharField(widget=forms.HiddenInput())
    seller_name = forms.CharField(widget=forms.HiddenInput())
    shop_id = forms.CharField(widget=forms.HiddenInput())

