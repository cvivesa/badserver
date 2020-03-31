import django_tables2 as tables

from .models import *


class FutureTable(tables.Table):
    lot = tables.Column(linkify=True)

    class Meta:
        model = Future
        fields = ("lot", "start_time", "end_time", "request_expiration_time", "price")


class AcceptedFutureTable(tables.Table):
    class Meta:
        model = Future
        fields = ("spot","start_time", "end_time")


class OptionTable(tables.Table):
    lot = tables.Column(linkify=True)

    class Meta:
        model = Option
        fields = (
            "lot",
            "start_time",
            "end_time",
            "request_expiration_time",
            "price",
            "fee",
            "collateral",
        )

class AcceptedOptionTable(tables.Table):
    lot = tables.Column(linkify=True)

    class Meta:
        model = Option
        fields = (
            "lot",
            "start_time",
            "end_time",
            "price",
            #TODO Add way to find market value of spot (average of 3 last spots sold)
        )
class GroupTable(tables.Table):
    class Meta:
        model = Group
        fields = ("name", "fee", "minimum_price", "minimum_ratio")
