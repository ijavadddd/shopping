from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from django.db.models import Q
from shopping.dashboard.utils import get_model_properties
from django.core.exceptions import ObjectDoesNotExist
from shopping.dashboard.paginations import DashboardPagination


class DashboardTableAPI(APIView):
    pagination_class = DashboardPagination

    def get(self, request):
        model_name = request.query_params.get("model")
        search = request.query_params.get("search")
        sort = request.query_params.get("sort")
        method = request.query_params.get("method", "list")
        page_size = int(request.query_params.get("page_size", 15))

        Model, serializer = get_model_properties(model_name, method)
        if not Model:
            return Response(
                {"error": "Invalid model"}, status=status.HTTP_400_BAD_REQUEST
            )
        qs = Model.objects.all()

        # Search in all Char/Text fields
        if search:
            search_fields = [
                f.name
                for f in Model._meta.fields
                if f.get_internal_type() in ["CharField", "TextField"]
            ]
            q_objects = Q()
            for field in search_fields:
                q_objects |= Q(**{f"{field}__icontains": search})
            qs = qs.filter(q_objects)

        # Sorting
        if sort:
            qs = qs.order_by(sort)

        # Pagination
        paginator = self.pagination_class()
        paginator.page_size = page_size
        result_page = paginator.paginate_queryset(qs, request)

        data = [
            {field.name: getattr(obj, field.name) for field in Model._meta.fields}
            for obj in result_page
        ]
        serializer = serializer(qs, many=True)
        return Response(serializer.data)

        # return paginator.get_paginated_response(data.data)

    def post(self, request):
        """Create a new record"""
        model_name = request.data.get("model")
        Model = get_model_properties(model_name)
        if not Model:
            return Response(
                {"error": "Invalid model"}, status=status.HTTP_400_BAD_REQUEST
            )

        obj = Model.objects.create(**request.data.get("data", {}))
        return Response({"id": obj.pk, "message": "Created successfully"})

    def put(self, request):
        """Edit an existing record"""
        model_name = request.data.get("model")
        obj_id = request.data.get("id")
        Model = get_model_properties(model_name)
        if not Model:
            return Response(
                {"error": "Invalid model"}, status=status.HTTP_400_BAD_REQUEST
            )

        try:
            obj = Model.objects.get(pk=obj_id)
        except ObjectDoesNotExist:
            return Response(
                {"error": "Object not found"}, status=status.HTTP_404_NOT_FOUND
            )

        for k, v in request.data.get("data", {}).items():
            setattr(obj, k, v)
        obj.save()
        return Response({"message": "Updated successfully"})

    def delete(self, request):
        """Delete record(s)"""
        model_name = request.data.get("model")
        ids = request.data.get("ids", [])
        Model = get_model_properties(model_name)
        if not Model:
            return Response(
                {"error": "Invalid model"}, status=status.HTTP_400_BAD_REQUEST
            )

        deleted, _ = Model.objects.filter(pk__in=ids).delete()
        return Response({"message": f"Deleted {deleted} records"})
