import django_tables2 as tables

from .models import Future


class FutureTable(tables.Table):
    lot = tables.Column(linkify=True)

    class Meta:
        model = Future
        fields = ("lot", "start_time", "end_time", "request_expiration_time", "price")
        attrs = {"class": "table"}


class AcceptedFutureTable(tables.Table):
    class Meta:
        model = Future
        fields = ("lot", "start_time", "end_time")
        attrs = {"class": "table"}
