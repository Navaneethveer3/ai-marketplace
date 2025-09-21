from django.shortcuts import render
from rest_framework import viewsets, status
from rest_framework.decorators import action, api_view, permission_classes   # ✅ add action here
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.shortcuts import get_object_or_404
from .models import Artisan, Product, Cart, CartItem, Order
from .serializers import ArtisanSerializer, ProductSerializer, CartSerializer, OrderSerializer
from django.contrib.auth.models import User

class ArtisanViewSet(viewsets.ModelViewSet):
    queryset = Artisan.objects.all().order_by("-id")
    serializer_class = ArtisanSerializer
    filterset_fields = ["craft_type", "name"]


class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all().order_by("-id")
    serializer_class = ProductSerializer
    permission_classes = [AllowAny]






class CartViewSet(viewsets.ViewSet):
    permission_classes = [AllowAny]

    def get_cart(self):
    # Use a dummy user with username "demo"
        user, _ = User.objects.get_or_create(username="demo")
        cart, _ = Cart.objects.get_or_create(user=user)
        return cart

    def list(self, request):
        cart = self.get_cart()
        serializer = CartSerializer(cart)
        return Response(serializer.data)

    @action(detail=False, methods=["post"])
    def add_item(self, request):
        cart = self.get_cart()
        product_id = request.data.get("product_id")
        quantity = int(request.data.get("quantity", 1))

        product = get_object_or_404(Product, id=product_id)
        item, created = CartItem.objects.get_or_create(cart=cart, product=product)
        if not created:
            item.quantity += quantity
        else:
            item.quantity = quantity
        item.save()

        return Response(CartSerializer(cart).data, status=status.HTTP_201_CREATED)

    @action(detail=False, methods=["post"])
    def remove_item(self, request):
        cart = self.get_cart()
        product_id = request.data.get("product_id")
        item = get_object_or_404(CartItem, cart=cart, product_id=product_id)
        item.delete()
        return Response(CartSerializer(cart).data)


class OrderViewSet(viewsets.ViewSet):
    permission_classes = [AllowAny]

    def list(self, request):
        # Dummy user for prototype
        orders = Order.objects.filter(user_id=1)
        return Response(OrderSerializer(orders, many=True).data)

    @action(detail=False, methods=["post"])
    def checkout(self, request):
        cart, _ = Cart.objects.get_or_create(user_id=1)
        if not cart.items.exists():
            return Response({"error": "Cart is empty"}, status=400)

        total = sum(item.product.price * item.quantity for item in cart.items.all())
        order = Order.objects.create(user_id=1, total_price=total)

        # clear cart
        cart.items.all().delete()

        return Response(OrderSerializer(order).data, status=201)
