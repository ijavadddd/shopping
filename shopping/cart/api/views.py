from rest_framework.viewsets import ModelViewSet

from shopping import cart
from shopping.cart.api.serializers import (
    CartSerializer,
    CartCreateSerializer,
    CartItemSerializer,
)
from shopping.cart.models import Cart, Item
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework import status
from rest_framework.generics import RetrieveAPIView
from rest_framework.views import APIView


class CartAPIView(APIView):
    serializer_class = CartCreateSerializer
    permission_classes = [AllowAny]
    # queryset = Cart.objects.all()
    # lookup_field = 'pk'

    def get_serializer_class(self):
        if self.request.method == "PUT":
            return CartCreateSerializer
        if self.request.method == "GET":
            return CartSerializer

    def get_queryset(self):
        cart = (
            Cart.objects.filter(user=self.request.user)
            .prefetch_related(
                "items__product", "items__variation", "items__product__images"
            )
            .first()
        )
        return cart

    def get(self, request, *args, **kwargs):
        cart = self.get_queryset()
        return Response(CartSerializer(cart).data)

    def put(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        cart = serializer.save(user=self.request.user)
        return Response(CartSerializer(cart).data)


from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from django.db import transaction
from django.shortcuts import get_object_or_404


class CartRemoveAPIView(APIView):
    permission_classes = [AllowAny]

    def get_serializer_class(self):
        return CartItemSerializer if self.request.method == "POST" else CartSerializer

    @transaction.atomic
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer_class()(data=request.data)
        serializer.is_valid(raise_exception=True)
        validated_data = serializer.validated_data

        # Get cart or return 404 if not found
        cart = get_object_or_404(Cart, user=request.user)

        # Get item with select_for_update to lock the row
        item = (
            Item.objects.filter(
                cart=cart,
                product=validated_data["product"],
                variation=validated_data.get("variation"),
            )
            .select_for_update()
            .first()
        )

        if item:
            quantity_to_remove = validated_data["quantity"]

            # If removing all or more than available
            if quantity_to_remove >= item.quantity:
                item.delete()
            else:
                item.quantity -= quantity_to_remove
                item.save()

        # Return refreshed cart data
        return Response(
            CartSerializer(cart, context={"request": request}).data, status=200
        )
