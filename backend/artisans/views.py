from django.shortcuts import render
from rest_framework import viewsets, status
from rest_framework.decorators import action, api_view, permission_classes   # ✅ add action here
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.shortcuts import get_object_or_404
from .models import Artisan, Product, Cart, CartItem, Order
from .serializers import ArtisanSerializer, ProductSerializer, CartSerializer, OrderSerializer
#from .ai_utils import generate_ai_text
import os
import openai

# Configure OpenAI API Key from ENV
OPENAI_KEY = os.getenv("OPENAI_API_KEY")
if OPENAI_KEY:
    openai.api_key = OPENAI_KEY

class ArtisanViewSet(viewsets.ModelViewSet):
    queryset = Artisan.objects.all().order_by("-id")
    serializer_class = ArtisanSerializer
    filterset_fields = ["craft_type", "name"]


class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all().order_by("-id")
    serializer_class = ProductSerializer
    permission_classes = [AllowAny]


@api_view(["POST"])
@permission_classes([AllowAny])
def ai_generate(request):
    """
    Expect JSON:
    {
      "type": "product" | "story",
      "input": "short product description or artisan story"
    }
    Returns generated marketing text (description, caption, tagline)
    """
    data = request.data
    typ = data.get("type", "product")
    text = data.get("input", "")
    if not text:
        return Response({"error": "No input provided"}, status=400)

    if not OPENAI_KEY:
        # graceful fallback
        if typ == "product":
            return Response({"description": f"Polished: {text}", "caption": f"Buy this: {text[:60]}..."})
        else:
            return Response({"summary": text[:200], "tagline": text[:60]})

    try:
        if typ == "product":
            prompt = f"Rewrite and expand this product blurb into a short marketing product description (2 paragraphs), and provide 3 short social captions (one-line each). Input: {text}"
            messages = [
                {"role": "system", "content": "You are a helpful marketing assistant."},
                {"role": "user", "content": prompt},
            ]
            resp = openai.ChatCompletion.create(model="gpt-4o-mini", messages=messages, max_tokens=300)
            gen = resp["choices"][0]["message"]["content"]
            # Basic parsing: return whole content as description (for prototype)
            return Response({"generated": gen})
        else:
            prompt = f"Summarize this artisan story in 2-3 lines for a marketplace, and then provide a tagline (max 6 words). Input: {text}"
            messages = [
                {"role": "system", "content": "You are a creative content assistant."},
                {"role": "user", "content": prompt},
            ]
            resp = openai.ChatCompletion.create(model="gpt-4o-mini", messages=messages, max_tokens=200)
            gen = resp["choices"][0]["message"]["content"]
            return Response({"generated": gen})
    except Exception as e:
        return Response({"error": str(e)}, status=500)



class CartViewSet(viewsets.ViewSet):
    permission_classes = [AllowAny]

    def get_cart(self):
        # For prototype, always use dummy user with id=1
        cart, _ = Cart.objects.get_or_create(user_id=1)
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
