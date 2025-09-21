"""
URL configuration for artisan_marketplace project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from rest_framework import routers
from artisans.views import ArtisanViewSet, ProductViewSet, CartViewSet, OrderViewSet, ai_generate
from django.conf import settings
from django.conf.urls.static import static
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView

router = routers.DefaultRouter()
router.register(r"artisans", ArtisanViewSet)
router.register(r"products", ProductViewSet)

cart_list = CartViewSet.as_view({"get": "list"})
cart_add = CartViewSet.as_view({"post": "add_item"})
cart_remove = CartViewSet.as_view({"post": "remove_item"})

order_list = OrderViewSet.as_view({"get": "list"})
order_checkout = OrderViewSet.as_view({"post": "checkout"})


urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/", include(router.urls)),
    path("api/cart/", cart_list, name="cart-list"),
    path("api/cart/add/", cart_add, name="cart-add"),
    path("api/cart/remove/", cart_remove, name="cart-remove"),
    path("api/orders/", order_list, name="order-list"),
    path("api/orders/checkout/", order_checkout, name="order-checkout"),
    path("api/ai/generate/", ai_generate),
     path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    path("api/docs/", SpectacularSwaggerView.as_view(url_name="schema")),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)