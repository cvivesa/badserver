from django.shortcuts import get_object_or_404
from rest_framework.generics import RetrieveAPIView
from rest_framework.response import Response

from parking.models import *


class FutureAPIView(RetrieveAPIView):
    def get(self, request, **kwargs):
        qs = (
            Future.objects.filter(buyer__isnull=False)
            .order_by("start_time")
            .values("price", "start_time")
        )

        return Response(qs)
