from rest_framework import serializers
from .models import Artisan, Product, Cart, CartItem, Order


class ProductSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(required=False)
    image = serializers.ImageField(required=False, allow_null=True)
    artisan = serializers.PrimaryKeyRelatedField(queryset=Artisan.objects.all())

    class Meta:
        model = Product
        fields = ["id", "artisan", "name", "price", "description", "image", "ai_description"]

class ArtisanSerializer(serializers.ModelSerializer):
    products = ProductSerializer(many=True, required=False)
    image = serializers.ImageField(required=False, allow_null=True)

    class Meta:
        model = Artisan
        fields = ["id", "name", "craft_type", "story", "image", "ai_tagline", "products"]

    def create(self, validated_data):
        products_data = validated_data.pop("products", [])
        artisan = Artisan.objects.create(**validated_data)

        # auto-generate tagline if missing
        

        for p in products_data:
            product = Product.objects.create(artisan=artisan, **p)
            
        return artisan

    def update(self, instance, validated_data):
        products_data = validated_data.pop("products", [])
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        keep_ids = []
        for p in products_data:
            if "id" in p:
                prod = Product.objects.get(id=p["id"], artisan=instance)
                for attr, value in p.items():
                    if attr != "id":
                        setattr(prod, attr, value)
                prod.save()
                keep_ids.append(prod.id)
            else:
                new_prod = Product.objects.create(artisan=instance, **p)
                keep_ids.append(new_prod.id)

        # delete removed products
        instance.products.exclude(id__in=keep_ids).delete()
        return instance

class CartItemSerializer(serializers.ModelSerializer):
    product = ProductSerializer(read_only=True)
    product_id = serializers.PrimaryKeyRelatedField(
        queryset=Product.objects.all(), source="product", write_only=True
    )

    class Meta:
        model = CartItem
        fields = ["id", "product", "product_id", "quantity"]


class CartSerializer(serializers.ModelSerializer):
    items = CartItemSerializer(many=True, read_only=True)

    class Meta:
        model = Cart
        fields = ["id", "user", "items"]


class OrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = ["id", "user", "created_at", "total_price"]
