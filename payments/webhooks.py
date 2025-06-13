import logging
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from liqpay.liqpay3 import LiqPay
from django.conf import settings
from django.http import HttpResponse, JsonResponse
from orders.models import Order
import json
from .verify_monobank_signature import verify_with_fallback


logger = logging.getLogger(__name__)

@csrf_exempt
@require_POST
def liqpay_webhook(request):
    logger.info(f'LIQPAY_PUBLIC_KEY={settings.LIQPAY_PUBLIC_KEY}')
    logger.info(f'LIQPAY_PRIVATE_KEY={settings.LIQPAY_PRIVATE_KEY}')
    liqpay = LiqPay(settings.LIQPAY_PUBLIC_KEY, settings.LIQPAY_PRIVATE_KEY)
    
    data = request.POST.get('data', '')
    signature = request.POST.get('signature')

    if not data or not signature:
        logger.warning("Получены пустые данные или подпись в webhook от LiqPay")
        return HttpResponse(status=400)
    
    expected_signature = liqpay.str_to_sign(settings.LIQPAY_PRIVATE_KEY + data + settings.LIQPAY_PRIVATE_KEY)
    
    if signature != expected_signature:
        logger.warning(f"Ошибка валидации подписи от LiqPay. Signature: {signature} != Expected signature: {expected_signature}")
        return HttpResponse(status=400)
    
    response = liqpay.decode_data_from_str(data)
    status = response.get('status')
    order_id = response.get('order_id')
    payment_id = response.get('payment_id')

    logger.info(f"LiqPay callback: order_id={order_id}, status={status}, payment_id={payment_id}")

    if status == 'success':
        try:
            o = Order.objects.get(id=order_id)
            o.paid = True
            o.liqpay_id = payment_id
            o.save()
            logger.info(f"Заказ {order_id} успешно оплачен через LiqPay")
        except Order.DoesNotExist:
            logger.error(f"Заказ {order_id} не найден")
            return HttpResponse(status=404)

    return JsonResponse({"status": "ok"})


@csrf_exempt
@require_POST
def monobank_webhook(request):
    x_sign = request.headers.get("X-Sign")
    if not x_sign:
        logger.warning("Відсутній заголовок X-Sign")
        return HttpResponse(status=400)

    if not verify_with_fallback(x_sign, request.body):
        logger.warning("Невірний підпис від Monobank")
        return HttpResponse(status=400)

    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return HttpResponse(status=400)

    reference = data.get("reference")
    status_ = data.get("status")
    invoice_id = data.get("invoiceId")

    if status_ == "success" and reference:
        try:
            order = Order.objects.get(id=reference)
            if not order.paid:
                order.paid = True
                order.monobank_id = invoice_id
                order.save()
                logger.info(f"Оплата успішна. Order ID: {reference}")
        except Order.DoesNotExist:
            logger.error(f"Order not found: {reference}")
            return HttpResponse(status=404)

    return JsonResponse({"status": "ok"})
