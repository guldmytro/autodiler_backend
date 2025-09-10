from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.views import APIView
from shop.models import Product, Category
from orders.models import Order, OrderOneClick
from faq.models import Faq
from blog.models import Post
from profiles.models import Profile
from .serializers import *
from .permissions import IsAdminOrReadOnly, IsAdminOrReadOrPost, CanPost
from rest_framework.filters import OrderingFilter
from django_filters import rest_framework as d_filters
from rest_framework.decorators import action
from django.template.loader import render_to_string
from django.conf import settings
from .telegram import send_telegram_message
from django.views.decorators.cache import cache_page
from django.utils.decorators import method_decorator
from rest_framework import generics
from rest_framework.pagination import PageNumberPagination
from seo.models import SeoItem
from django.contrib.postgres.search import TrigramSimilarity
from django.db.models import Q
import logging
from .magic_link import MagicLinkToken
from django.utils.translation import get_language
from rest_framework_simplejwt.tokens import UntypedToken, RefreshToken
from rest_framework_simplejwt.exceptions import TokenError
from profiles.models import Profile
from django.core.cache import cache
import hashlib
import json
import requests
from api.sendpulse_mailer import send_mail
from datetime import datetime

logger = logging.getLogger(__name__)


class NoPagination(PageNumberPagination):
    page_size = None


class ProductFilter(d_filters.FilterSet):
    id = d_filters.CharFilter(method='filters_by_ids')
    category = d_filters.CharFilter(method='filters_by_category_id__in')
    s = d_filters.CharFilter(method='filters_by_query')
    language_code = None

    def __init__(self, data=None, queryset=None, *, request=None, prefix=None):
        self.language_code = request.LANGUAGE_CODE if request else 'uk'
        super().__init__(data, queryset, request=request, prefix=prefix)

    def filters_by_ids(self, queryset, name, value):
        ids = value.split(',')
        return Product.objects.filter(id__in=ids)

    def filters_by_category_id__in(self, queryset, name, value):
        try:
            current_category = Category.objects.get(pk=int(value))
            descendants = list(
                current_category.get_descendants().values_list('id',
                                                               flat=True))
            descendants.append(int(value))
            return queryset.filter(category_id__in=descendants)
        except Category.DoesNotExist:
            return queryset.none()

    def filters_by_query(self, queryset, name, value):
        f_qs = queryset.filter(
            Q(translation__language_code=self.language_code) & (
                Q(translation__name__icontains=value) |
                Q(vin__icontains=value) |
                Q(producer__icontains=value) |
                Q(sku__icontains=value)
            )
        ).annotate(
            similarity=TrigramSimilarity('translation__name', value)
        ).filter(
            Q(similarity__gt=0.1) |
            Q(vin__icontains=value) |
            Q(producer__icontains=value) |
            Q(sku__icontains=value)
        ).order_by('-similarity')

        return f_qs

    class Meta:
        model = Product
        fields = ['id', 'category', 's']


class ProductViewSet(viewsets.ModelViewSet):
    permission_classes = (IsAdminOrReadOnly,)
    queryset = Product.objects.prefetch_related(
        'translation',
        # 'category__translation'
    ).select_related('category').exclude(
        Q(image__isnull=True) | Q(image=''),
        Q(image2__isnull=True) | Q(image2='')
    ).filter(quantity__gt=0).filter(category__visible=True)
    serializer_class = ProductSerializer
    filter_backends = [OrderingFilter, d_filters.DjangoFilterBackend]
    filterset_class = ProductFilter
    ordering_fields = ['created', 'price']
    lookup_field = 'slug'

    def is_partner(self, request):
        user = request.user
        return user.is_authenticated and hasattr(user, 'profile') and user.profile.partner

    def get_cache_key(self, request, suffix="list", extra=""):
        language = get_language()
        base = f"{suffix}:{'partner' if self.is_partner(request) else 'user'}"
        query = json.dumps(request.query_params, sort_keys=True)
        raw = f"{language}:{base}:{query}:{extra}"
        return hashlib.md5(raw.encode()).hexdigest()
    
    def list(self, request, *args, **kwargs):
        cache_key = self.get_cache_key(request, "list")
        cached_response = cache.get(cache_key)
        if cached_response:
            return Response(cached_response)

        response = super().list(request, *args, **kwargs)
        cache.set(cache_key, response.data, timeout=60 * 15)
        return response

    def retrieve(self, request, slug=None):
        cache_key = self.get_cache_key(request, "retrieve", extra=slug)
        cached_response = cache.get(cache_key)
        if cached_response:
            return Response(cached_response)

        response = super().retrieve(request, slug=slug)
        cache.set(cache_key, response.data, timeout=60 * 15)
        return response

    @action(detail=True, url_path='buy', methods=['post'],
            permission_classes=[CanPost])
    def buy_single(self, request, *args, **kwargs):
        obj = self.get_object()
        phone = request.data.get('phone', '')
        context = {
            'product': obj,
            'phone': phone,
        }
        message = render_to_string('emails/buy-single.html',
                                   context)
        to = settings.EMAIL_RECEPIENTS
        subject = 'Купівля в 1 клік'
        try:
            OrderOneClick.objects.create(phone=str(phone).strip(), product=obj)
        except Exception as e:

            logger.error(f'Помилка під час створвення замовлення в 1 клік: {e}')
            logger.error(f'phone: {str(phone).strip()} .')
        
        if send_telegram_message(message) == 1:
            return Response({'status': 'ok'})
        
        return Response({'status': 'bad'})

class ProductWithColorViewSet(viewsets.ModelViewSet):
    permission_classes = (IsAdminOrReadOnly,)
    queryset = Product.objects.prefetch_related(
        'translation',
        # 'category__translation'
    ).select_related('category').exclude(
        Q(parent__image__isnull=True) | Q(parent__image=''),
        Q(parent__image2__isnull=True) | Q(parent__image2='')
    ).exclude(parent__isnull=True).filter(parent__quantity__gt=0)
    serializer_class = ProductWithColorSerializer
    lookup_field = 'slug'


class OrderViewSet(viewsets.ModelViewSet):
    permission_classes = (IsAdminOrReadOrPost,)
    queryset = Order.objects.prefetch_related('items')
    serializer_class = OrderSerializer

    def perform_create(self, serializer):
        user = self.request.user if self.request.user.is_authenticated else None
        serializer.save(user=user)
    
    @action(detail=True, methods=['post'], url_path='get_monobank_link')
    def get_monobank_link(self, request, pk=None):
        order = self.get_object()

        if order.paid:
            return Response(
                {'detail': 'Це замовлення вже оплачене.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        headers = {
            'X-Token': settings.MONOBANK_TOKEN,
            'Content-Type': 'application/json'
        }

        payload = {
            'amount': int(order.get_total_cost() * 100),
            'ccy': 980,
            'redirectUrl': f'https://avtodiler.com.ua/checkout/success/{order.id}',
            'webHookUrl': 'https://api.avtodiler.com.ua/payment/webhook-mono/',
            'merchantPaymInfo': {
                'reference': str(order.id),
                'destination': f'Замовлення №{order.id}',
                'customerEmails': [order.email],
                'basketOrder': [
                    {
                        'name': item.product.name,
                        'qty': item.quantity,
                        'sum': int(item.price * 100),
                        'total': int(item.get_cost() * 100),
                        'unit': 'шт.',
                        'code': str(item.product.id),
                        'icon': f"https://api.avtodiler.com.ua{item.product.image.url}" if item.product.image and item.product.image.name else ''
                    } for item in order.items.all()
                ]
            }
        }

        try:
            response = requests.post(
                'https://api.monobank.ua/api/merchant/invoice/create',
                headers=headers,
                json=payload,
                timeout=10
            )
        except requests.RequestException as e:
            return Response({'detail': str(e)}, status=status.HTTP_502_BAD_GATEWAY)
        
        return Response(response.json(), status=status.HTTP_200_OK)


class CategoryViewSet(viewsets.ModelViewSet):
    permission_classes = (IsAdminOrReadOnly,)
    queryset = Category.objects.filter(visible=True)
    serializer_class = CategorySerializer
    lookup_field = 'slug'

    @method_decorator(cache_page(60 * 60 * 2))
    def list(self, request):
        return super().list(request)

    @method_decorator(cache_page(60 * 60 * 2))
    def retrieve(self, request, slug=None):
        return super().retrieve(request, slug)

    @method_decorator(cache_page(60 * 60 * 2))
    @action(detail=False, url_path='dump', methods=['get'])
    def remind(self, request, *args, **kwargs):
        return Response(Category.dump_bulk())


class FaqViewSet(viewsets.ModelViewSet):
    permission_classes = (IsAdminOrReadOnly,)
    queryset = Faq.objects.prefetch_related(
        'translation',
    )
    serializer_class = FaqSerializer


class SendEmailView(APIView):
    permission_classes = [CanPost,]

    def post(self, request, *args, **kwargs):
        serializer = EmailSerializer(data=request.data)
        if serializer.is_valid():
            name = serializer.validated_data['name']
            phone = serializer.validated_data['phone']
            message = render_to_string('emails/feadback.html', {
                'name': name,
                'phone': phone
            })
            subject = 'Не знайшли потрібну деталь'
            to = settings.EMAIL_RECEPIENTS

            if send_telegram_message(message) == 1:
                return Response({'status': 'ok',
                                'message': 'Email sent successfully'})
            
            return Response({'status': 'bad'},
                            status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response(serializer.errors,
                            status=status.HTTP_400_BAD_REQUEST)


class SendDSEmailView(APIView):
    permission_classes = [CanPost,]

    def post(self, request, *args, **kwargs):
        serializer = DropshippingEmailSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data['email']
            phone = serializer.validated_data['phone']
            message = render_to_string('emails/dropshipping-feadback.html', {
                'email': email,
                'phone': phone
            })
            subject = 'Користувач хоче отримати прайс-лист для партнерів'
            to = settings.EMAIL_RECEPIENTS
            
            if send_telegram_message(message) == 1:
                return Response({'status': 'ok',
                                 'message': 'Email sent successfully'})
            
            return Response({'status': 'bad'},
                            status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response(serializer.errors,
                            status=status.HTTP_400_BAD_REQUEST)


class TakeOfferEmailView(APIView):
    permission_classes = [CanPost,]

    def post(self, request, *args, **kwargs):
        serializer = TakeOfferEmailSerializer(data=request.data)
        if serializer.is_valid():
            name = serializer.validated_data['name']
            phone = serializer.validated_data['phone']
            city = serializer.validated_data['city']
            client_type = serializer.validated_data['clientType']
            product_type = serializer.validated_data['productType']
            message = render_to_string('emails/take-offer.html', {
                'name': name,
                'phone': phone,
                'city': city,
                'client_type': client_type,
                'product_type': product_type
            })
            subject = 'Користувач хоче отримати прайс-лист для партнерів'
            to = settings.EMAIL_RECEPIENTS
            if send_telegram_message(message) == 1:
                return Response({'status': 'ok',
                                'message': 'Email sent successfully'})
            
            return Response({'status': 'bad'},
                            status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response(serializer.errors,
                            status=status.HTTP_400_BAD_REQUEST)


class BlogViewSet(viewsets.ModelViewSet):
    permission_classes = (IsAdminOrReadOnly,)
    queryset = Post.objects.all()
    serializer_class = PostSerializer


class ProfileView(APIView):
    def get(self, request):
        if request.user.is_authenticated:
            profile = Profile.objects.get(user=request.user)
            serializer = ProfileSerializer(profile)
            return Response(serializer.data)

    def put(self, request):
        profile = Profile.objects.get(user=request.user)
        serializer = ProfileSerializer(profile, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=400)


class MyOrderViewSet(viewsets.ModelViewSet):
    serializer_class = MyOrderSerializer

    def get_queryset(self):
        user = self.request.user
        return Order.objects.filter(user=user)


class ProductSitemap(generics.ListAPIView):
    queryset = Product.objects.exclude(image__isnull=True).exclude(image='').filter(quantity__gt=0)
    serializer_class = ProductSitemapSerializer
    permission_classes = (IsAdminOrReadOnly,)
    pagination_class = NoPagination


class ProductMerchant(generics.ListAPIView):
    queryset = Product.objects.exclude(image__isnull=True).exclude(image='')\
                      .filter(quantity__gt=0).filter(category__visible=True)
                      #.filter(created__lte=datetime(2025, 7, 23, 23, 59, 59))
    serializer_class = ProductMerchantSerializer
    permission_classes = (IsAdminOrReadOnly,)
    pagination_class = NoPagination

    @method_decorator(cache_page(60 * 60 * 6))
    def list(self, request):
        return super().list(request)


class CategorySitemap(generics.ListAPIView):
    queryset = Category.objects.filter(visible=True)
    serializer_class = CategorySitemapSerializer
    permission_classes = (IsAdminOrReadOnly,)
    pagination_class = NoPagination


class SeoFilter(d_filters.FilterSet):
    class Meta:
        model = SeoItem
        fields = ['link']


class SeoAPiView(generics.ListAPIView):
    queryset = SeoItem.objects.all()
    permission_classes = (IsAdminOrReadOnly,)
    pagination_class = NoPagination
    serializer_class = SeoSerializer
    filter_backends = [OrderingFilter, d_filters.DjangoFilterBackend]
    filterset_class = SeoFilter



from django.http import HttpResponse
from xml.etree.ElementTree import Element, SubElement, tostring
from cml.auth import *
from django.views.decorators.csrf import csrf_exempt
from datetime import date
from django.utils import timezone

@csrf_exempt
@has_perm_or_basicauth('cml.add_exchange')
@logged_in_or_basicauth()
def export_orders_to_xml(request):
    orders = Order.objects.prefetch_related('items__product').all()

    root = Element("КоммерческаяИнформация", ВерсияСхемы="2.03", ДатаФормирования=str(date.today()))

    for order in orders:
        order_el = SubElement(root, 'Документ')
        local_created = timezone.localtime(order.created).replace(microsecond=0)

        SubElement(order_el, 'Ид').text = str(order.id)
        SubElement(order_el, 'Номер').text = str(order.id)
        SubElement(order_el, 'Дата').text = local_created.date().isoformat()
        SubElement(order_el, 'Время').text = local_created.time().isoformat()
        SubElement(order_el, 'ХозОперация').text = 'Заказ товара'
        SubElement(order_el, 'Роль').text = 'Продавец'
        SubElement(order_el, 'Валюта').text = 'UAH'
        SubElement(order_el, 'Курс').text = '1'
        SubElement(order_el, 'Сумма').text = f"{order.get_total_cost():.2f}"
        SubElement(order_el, 'СрокПлатежа').text = local_created.date().isoformat()

        kontrs = SubElement(order_el, "Контрагенты")
        kontr = SubElement(kontrs, "Контрагент")
        SubElement(kontr, "Ид").text = ''
        SubElement(kontr, "Наименование").text = f'{order.last_name} {order.first_name}'
        SubElement(kontr, "Роль").text = "Покупатель"
        rekv = SubElement(kontr, "РеквизитыФизЛица")
        SubElement(rekv, "ПолноеНаименование").text = f'{order.last_name} {order.first_name}'
        SubElement(rekv, "Телефон").text = order.clean_phone()
        SubElement(rekv, "Почта").text = order.email

        SubElement(order_el, 'Комментарий').text = f'{order.clean_phone()} | {order.email}'
        

        # Товары
        products = SubElement(order_el, "Товары")

        for item in order.items.all():
            item_el = SubElement(products, 'Товар')
            SubElement(item_el, "Ид").text = item.product.id_1c
            SubElement(item_el, "Артикул").text = ''
            SubElement(item_el, "Наименование").text = item.product.name
            base_unit = SubElement(item_el, "БазоваяЕдиница", {
                "Код": item.product.sku,
                "НаименованиеПолное": "шт",
                "МеждународноеСокращение": "PCE"
            })
            base_unit.text = "шт"

            z_rekv = SubElement(item_el, "ЗначенияРеквизитов")
            for name in ["ВидНоменклатуры", "ТипНоменклатуры"]:
                val = SubElement(z_rekv, "ЗначениеРеквизита")
                SubElement(val, "Наименование").text = name
                SubElement(val, "Значение").text = "Товар"

            taxes = SubElement(item_el, "СтавкиНалогов")
            tax = SubElement(taxes, "СтавкаНалога")
            SubElement(tax, "Наименование").text = "НДС"
            SubElement(tax, "Ставка").text = "20"

            SubElement(item_el, "ЦенаЗаЕдиницу").text = f"{item.price:.2f}"
            SubElement(item_el, "Количество").text = str(item.quantity)
            SubElement(item_el, "Сумма").text = f'{item.get_cost():.2f}'
            SubElement(item_el, "Единица").text = "шт"
            SubElement(item_el, "Коэффициент").text = "1"

            nalogi = SubElement(item_el, "Налоги")
            nds = SubElement(nalogi, "Налог")
            SubElement(nds, "Наименование").text = "НДС"
            SubElement(nds, "Ставка").text = "Без налога"
            SubElement(nds, "УчтеноВСумме").text = "false"
            SubElement(nds, "Сумма").text = "0"

    xml_string = tostring(root, encoding='utf-8')
    return HttpResponse(xml_string, content_type='application/xml')


class SendMagicLinkView(APIView):
    permission_classes = [CanPost,]

    def post(self, request):
        serializer = SendMagicLinkSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        email = serializer.validated_data['email']

        token = MagicLinkToken()
        token['email'] = email

        lang = 'ru/' if get_language() == 'ru' else ''

        magic_link = f'{settings.CORS_ALLOWED_ORIGINS[3]}/{lang}account/login/confirm/{str(token)}'

        if send_mail(subject='Avtodiler.com.ua: Ваше посилання для входу',
                     message=f'Перейдіть по посиланню для входу в особистий кабінет: {magic_link}',
                     recipient_list=[email]):
            return Response({
                'status': 'ok',
                'message': 'Лист надіслано',
                'email': email
            }, status=status.HTTP_200_OK)
        
        return Response({'status': 'bad'}, status=status.HTTP_400_BAD_REQUEST)
    

class ConfirmMagicLink(APIView):
    permission_classes = []


    def get(self, request, token):
        try:
            magic_token = UntypedToken(token)
            if magic_token.payload.get('token_type') != 'magic':
                return Response({'error': 'Невірний тип токена'}, 
                                status=status.HTTP_400_BAD_REQUEST)
            email = magic_token.payload.get('email')
            if not email:
                return Response({'error': 'Email не знайдено в токені'}, 
                                status=status.HTTP_400_BAD_REQUEST)
            user, created = User.objects.get_or_create(
                username=email,
                defaults={'username': email, 'email': email}
            )

            if created:
                Profile.objects.create(user=user)
            
            refresh = RefreshToken.for_user(user)

            return Response({
                'refresh': str(refresh),
                'access': str(refresh.access_token),
                'is_new_user': created
            })

        except TokenError:
            return Response({'error': 'Невалідний або просрочений токен'}, 
                            status=status.HTTP_400_BAD_REQUEST)


class GoogleOrderViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Order.objects.all()
    serializer_class = GoogleOrderSerializer
    permission_classes = (IsAdminOrReadOnly,)

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()

        serializer = self.get_serializer(instance)
        response = Response(serializer.data, status=status.HTTP_200_OK)

        if not instance.passed_to_google:
            instance.passed_to_google = True
            instance.save(update_fields=['passed_to_google'])

        return response