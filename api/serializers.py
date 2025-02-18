from shop.models import Product, Category
from orders.models import Order, OrderItem
from faq.models import Faq
from blog.models import Post
from profiles.models import Profile
from rest_framework import serializers
from drf_dynamic_fields import DynamicFieldsMixin
from shop.recommender import Recommender
from django.contrib.auth.models import User
from seo.models import SeoItem


class CategorySerializer(DynamicFieldsMixin, serializers.ModelSerializer):
    parents = serializers.SerializerMethodField()
    tree = serializers.SerializerMethodField()

    class Meta:
        model = Category
        fields = ('id', 'name_ua', 'name_ru', 'slug', 'parents', 'tree')

    def get_parents(self, obj):
        ancestors = obj.get_ancestors()
        # Convert queryset to a list of dictionaries
        parents_list = [{'id': ancestor.id, 'name_ua': ancestor.name_ua,
                         'name_ru': ancestor.name_ru, 'slug': ancestor.slug} for ancestor in
                        ancestors]
        return parents_list

    def get_tree(self, obj):
        return Category.dump_bulk(parent=obj)


class ProductSerializer(DynamicFieldsMixin, serializers.ModelSerializer):
    category = CategorySerializer()
    term_slug = serializers.SerializerMethodField()
    recommended_products = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = ('id', 'sku', 'name', 'slug', 'description', 'price', 'image',
                  'quantity', 'term_slug', 'category', 'producer', 'country',
                  'params', 'recommended_products')

    def get_recommended_products(self, obj):
        request = self.context.get('request')
        r = Recommender()
        return r.suggest_products_for([obj], 12,
                                      request=request)

    def get_term_slug(self, obj):
        try:
            return obj.category.slug
        except:
            return None


class OrderItemSerializer(serializers.ModelSerializer):

    class Meta:
        model = OrderItem
        fields = ('id', 'order', 'product', 'price', 'quantity')
        extra_kwargs = {
            'order': {'allow_null': True, 'required': False},
            'product': {'allow_null': False, 'required': True},
            'price': {'allow_null': False, 'required': True},
            'quantity': {'allow_null': False, 'required': True},
        }


class OrderSerializer(DynamicFieldsMixin, serializers.ModelSerializer):
    items = OrderItemSerializer(many=True)

    class Meta:
        model = Order
        fields = ('id', 'status', 'first_name', 'last_name', 'phone', 'email',
                  'delivery', 'city', 'nova_office', 'payment_method',
                  'comment', 'user_uuid', 'items', 'user')

    def create(self, validated_data):
        items_data = validated_data.pop('items')
        order = Order.objects.create(**validated_data)
        r = Recommender()
        p_bought = []
        for item_data in items_data:
            OrderItem.objects.create(order=order, **item_data)
            p_bought.append(item_data['product'])
        r.products_bought(p_bought)
        return order


class MyOrderItemSerializer(serializers.ModelSerializer):
    product = ProductSerializer()

    class Meta:
        model = OrderItem
        fields = ('id', 'order', 'product', 'price', 'quantity')


class MyOrderSerializer(DynamicFieldsMixin, serializers.ModelSerializer):
    items = MyOrderItemSerializer(many=True)

    class Meta:
        model = Order
        fields = ('id', 'status', 'first_name', 'last_name', 'phone', 'email',
                  'delivery', 'city', 'nova_office', 'payment_method',
                  'comment', 'items', 'created')


class FaqSerializer(serializers.ModelSerializer):
    class Meta:
        model = Faq
        fields = ('question', 'answer')


class EmailSerializer(serializers.Serializer):
    name = serializers.CharField()
    phone = serializers.CharField()


class DropshippingEmailSerializer(serializers.Serializer):
    email = serializers.CharField()
    phone = serializers.CharField()


class TakeOfferEmailSerializer(serializers.Serializer):
    clientType = serializers.CharField()
    productType = serializers.CharField()
    name = serializers.CharField()
    phone = serializers.CharField()
    city = serializers.CharField()


class PostSerializer(DynamicFieldsMixin, serializers.ModelSerializer):
    class Meta:
        model = Post
        fields = ('id', 'title', 'excerpt', 'body', 'created', 'updated',
                  'thumbnail',)


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('email',)


class ProfileSerializer(serializers.ModelSerializer):

    class Meta:
        model = Profile
        fields = ('first_name', 'last_name', 'phone')


class ProductSitemapSerializer(serializers.ModelSerializer):
    term_slug = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = ('slug', 'updated', 'term_slug')

    def get_term_slug(self, obj):
        try:
            return obj.category.slug
        except:
            return None


class ProductMerchantSerializer(serializers.ModelSerializer):
    term_slug = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = ('id', 'name', 'description', 'slug', 'term_slug', 
                  'image', 'quantity', 'price', 'producer')

    def get_term_slug(self, obj):
        try:
            return obj.category.slug
        except:
            return None


class CategorySitemapSerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ('slug', 'updated')


class SeoSerializer(serializers.ModelSerializer):

    class Meta:
        model = SeoItem
        fields = '__all__'



