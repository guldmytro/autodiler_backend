from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.views import APIView
from shop.models import Product, Category
from orders.models import Order
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
from django.core.mail import send_mail
from django.views.decorators.cache import cache_page
from django.utils.decorators import method_decorator
from rest_framework import generics
from rest_framework.pagination import PageNumberPagination
from seo.models import SeoItem
from django.contrib.postgres.search import TrigramSimilarity
from django.db.models import Q


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
        return queryset.filter(id__in=ids)

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
    ).select_related('category').exclude(image__isnull=True).exclude(image='')
    serializer_class = ProductSerializer
    filter_backends = [OrderingFilter, d_filters.DjangoFilterBackend]
    filterset_class = ProductFilter
    ordering_fields = ['created', 'price']
    lookup_field = 'slug'

    @method_decorator(cache_page(60 * 15))
    def list(self, request):
        return super().list(request)

    @method_decorator(cache_page(60 * 15))
    def retrieve(self, request, slug=None):
        return super().retrieve(request, slug)

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
        if send_mail(subject,
                     '',
                     'info.autodealer.ua@gmail.com',
                     to,
                     html_message=message) == 1:
            return Response({'status': 'ok'})
        return Response({'status': 'bad'})


class OrderViewSet(viewsets.ModelViewSet):
    permission_classes = (IsAdminOrReadOrPost,)
    queryset = Order.objects.prefetch_related('items')
    serializer_class = OrderSerializer

    def perform_create(self, serializer):
        user = self.request.user if self.request.user.is_authenticated else None
        serializer.save(user=user)


class CategoryViewSet(viewsets.ModelViewSet):
    permission_classes = (IsAdminOrReadOnly,)
    queryset = Category.objects.all()
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
            if send_mail(subject,
                         '',
                         'info.autodealer.ua@gmail.com', to,
                         html_message=message) == 1:
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
            if send_mail(subject,
                         '',
                         'info.autodealer.ua@gmail.com', to,
                         html_message=message) == 1:
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
            if send_mail(subject,
                         '',
                         'info.autodealer.ua@gmail.com', to,
                         html_message=message) == 1:
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
    queryset = Product.objects.all()
    serializer_class = ProductSitemapSerializer
    permission_classes = (IsAdminOrReadOnly,)
    pagination_class = NoPagination


class ProductMerchant(generics.ListAPIView):
    queryset = Product.objects.exclude(image__isnull=True).exclude(image='').filter(quantity__gt=0)
    serializer_class = ProductMerchantSerializer
    permission_classes = (IsAdminOrReadOnly,)
    pagination_class = NoPagination

    @method_decorator(cache_page(60 * 60 * 6))
    def list(self, request):
        return super().list(request)


class CategorySitemap(generics.ListAPIView):
    queryset = Category.objects.all()
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

@csrf_exempt
@has_perm_or_basicauth('cml.add_exchange')
@logged_in_or_basicauth()
def export_orders_to_xml(request):
    orders = Order.objects.prefetch_related('items__product').all()

    root = Element('Orders')

    for order in orders:
        order_el = SubElement(root, 'Order')
        SubElement(order_el, 'Id').text = str(order.id)
        SubElement(order_el, 'FirstName').text = order.first_name
        SubElement(order_el, 'LastName').text = order.last_name
        SubElement(order_el, 'Phone').text = order.clean_phone()
        SubElement(order_el, 'Email').text = order.email
        SubElement(order_el, 'Delivery').text = order.get_delivery_display()
        SubElement(order_el, 'City').text = order.city
        SubElement(order_el, 'Address').text = order.address or ''
        SubElement(order_el, 'TTN').text = order.ttn or ''
        SubElement(order_el, 'PaymentMethod').text = order.get_payment_method_display()
        SubElement(order_el, 'Paid').text = str(order.paid)
        SubElement(order_el, 'Comment').text = order.comment
        SubElement(order_el, 'Created').text = order.created.isoformat()
        SubElement(order_el, 'Updated').text = order.updated.isoformat()

        items_el = SubElement(order_el, 'Items')

        for item in order.items.all():
            item_el = SubElement(items_el, 'Item')
            SubElement(item_el, 'SKU').text = item.product.sku
            SubElement(item_el, 'ProductName').text = item.product.name
            SubElement(item_el, 'Quantity').text = str(item.quantity)
            SubElement(item_el, 'Price').text = str(item.price)
            SubElement(item_el, 'Total').text = str(item.get_cost())

    xml_string = tostring(root, encoding='utf-8')
    return HttpResponse(xml_string, content_type='application/xml')