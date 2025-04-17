from rest_framework.viewsets import ModelViewSet

from shopping.cart.api.serializers import CartSerializer
from shopping.cart.models import Cart
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status


class CartAPIViewSet(ModelViewSet):
    http_method_names = ["get", "post"]
    serializer_class = CartSerializer
    permission_classes = [IsAuthenticated]
    lookup_url_kwarg = "pk"
    # queryset = Cart.objects.all()

    def list(self, request, *args, **kwargs):
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)

    def get_queryset(self):
        if self.action == "retrieve":
            cart = Cart.objects.filter(
                user=self.request.user, pk=self.kwargs["pk"]
            ).prefetch_related(
                "items__product", "items__variation", "items__product__images"
            )
            return cart
