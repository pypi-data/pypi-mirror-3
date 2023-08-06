# -*- coding: utf-8 -*-
from hashlib import md5
from django.utils.encoding import smart_str

def calculate_hash(data, salt):
    """ Считаем хэш с солью по следующему принципу:
            hash = MD5(MD5(str_to_hash) + salt)
        Строка str_to_hash формируется конкатенацией следующих параметров запроса:
            order_id + order_total + transaction_id + payer_email + seller_name + shop_id
    """

    # эта строка управляет порядком сборки строки для хэширования
    FIELDS_ORDER = ('order_id', 'order_total', 'transaction_id', 'payer_email', 'seller_name', 'shop_id')
    data_as_list = [str(data[field]) for field in FIELDS_ORDER]
    str_to_hash = smart_str(''.join(data_as_list), 'utf-8')

    return md5(str_to_hash + salt).hexdigest()

