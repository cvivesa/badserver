from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from rest_framework.response import Response

from parking.models import *


class FutureAPIView(APIView):
    def get(self, request, **kwargs):
        futures = Future.objects
        if (kwargs.get("pk", None)):
            futures = futures.filter(lot__pk=kwargs['pk'])

        futures_complete = (
            futures.filter(buyer__isnull=False, seller__isnull=False)
            .order_by("start_time")
            .values_list("price", "start_time", "end_time")
        )

        futures_incomplete = (
            futures.exclude(buyer__isnull=False, seller__isnull=False)
            .order_by("start_time")
            .values_list("price", "start_time", "end_time")
        )

        payload = [[
            (start, float(price) / (end - start).days)
            for (price, start, end) in l
        ] for l in (futures_complete, futures_incomplete)]

        return Response(payload)


class OptionAPIView(APIView):
    def get(self, request, **kwargs):
        futures = Future.objects
        options = Option.objects
        if (kwargs.get("pk", None)):
            futures = futures.filter(lot__pk=kwargs['pk'])
            options = options.filter(lot__pk=kwargs['pk'])

        futures_complete = (
            futures.filter(buyer__isnull=False, seller__isnull=False)
            .order_by("start_time")
            .values_list("price", "start_time", "end_time")
        )

        options_complete = (
            options.filter(buyer__isnull=False, seller__isnull=False)
            .order_by("start_time")
            .values_list("price", "start_time", "end_time")
        )

        payload = [[
            (start, float(price) / (end - start).days)
            for (price, start, end) in l
        ] for l in (futures_complete, futures_incomplete)]

        return Response(payload)
