from rest_framework.viewsets import ModelViewSet
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework import status
from rest_framework.generics import RetrieveAPIView
from rest_framework.views import APIView
from django.db import transaction
from django.shortcuts import get_object_or_404

from shopping import cart
from shopping.cart.api.serializers import (
    CartSerializer,
    CartCreateSerializer,
    CartItemSerializer,
    CartItemCreateSerializer,
)
from shopping.cart.models import Cart, CartItem


class CartAPIView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = CartSerializer

    def get_object(self):
        cart, _ = Cart.objects.get_or_create(user=self.request.user)
        cart = Cart.objects.prefetch_related(
            "items__product",
            "items__variation",
        ).get(pk=cart.pk)
        return cart

    def get_serializer_class(self):
        if self.request.method in ["POST", "PUT", "PATCH"]:
            return CartCreateSerializer
        return CartSerializer
