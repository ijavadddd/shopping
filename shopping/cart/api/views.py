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
        return cart

    def get_serializer_class(self):
        if self.request.method in ["POST", "PUT", "PATCH"]:
            return CartCreateSerializer
        return CartSerializer


class CartRemoveAPIView(generics.DestroyAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = CartItemCreateSerializer

    def get_object(self):
        cart = Cart.objects.get(user=self.request.user)
        product_id = self.request.data.get("product")
        attribute_id = self.request.data.get("attribute")

        try:
            return CartItem.objects.get(
                cart=cart,
                product_id=product_id,
                attribute_id=attribute_id,
            )
        except CartItem.DoesNotExist:
            raise generics.NotFound("Item not found in cart")
