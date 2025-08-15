from rest_framework.routers import SimpleRouter
from .views import *
from django.urls import path, include
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenBlacklistView
)


router = SimpleRouter()
router.register(r'products', ProductViewSet, basename='products')
router.register(r'products-with-colors', ProductWithColorViewSet, basename='products-with-colors')
router.register(r'orders', OrderViewSet, basename='orders')
router.register(r'my-orders', MyOrderViewSet, basename='my-orders')
router.register(r'category', CategoryViewSet, basename='category')
router.register(r'faq', FaqViewSet, basename='faq')
router.register(r'posts', BlogViewSet, basename='posts')
router.register(r'google-orders', GoogleOrderViewSet, basename='google-orders')

urlpatterns = router.urls
urlpatterns += [
    path('feadback/', SendEmailView.as_view(), name='feadback'),
    path('ds-1/', SendDSEmailView.as_view(), name='ds-1'),
    path('ds-2/', TakeOfferEmailView.as_view(), name='ds-2'),
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('token/blacklist/', TokenBlacklistView.as_view(),
         name='token_blacklist'),
    path('profiles/me/', ProfileView.as_view(), name='profile'),
    path(r'auth/', include('djoser.urls')),
    path(r'products-sitemap/', ProductSitemap.as_view(),
         name='product-sitemap'),
    path(r'products-merchant/', ProductMerchant.as_view(),
         name='product-merchant'),
    path(r'categories-sitemap/', CategorySitemap.as_view(),
         name='categories-sitemap'),
    path(r'seo/', SeoAPiView.as_view(), name='seo'),
    path(r'order.xml', export_orders_to_xml, name='orders-exchange'),
    path(r'send-magic-link/', SendMagicLinkView.as_view(), name='send_magic_link'),
    path(r'confirm-magic-link/<str:token>/', ConfirmMagicLink.as_view(), name='confirm_magic_link'),
]

