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
        fields = ("spot", "start_time", "end_time")


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
    put = tables.BooleanColumn(
        accessor=tables.utils.A("calculate_put"), orderable=False
    )

    class Meta:
        model = Option
        fields = (
            "lot",
            "start_time",
            "end_time",
            "price",
            "put"
            # TODO Add way to find market value of spot (average of 3 last spots sold)
        )


class GroupTable(tables.Table):
    name = tables.Column(linkify=("group_join", [tables.A("pk")]))

    class Meta:
        model = Group
        fields = ("name", "fee", "minimum_price", "minimum_ratio")


class UnfullFilledOptionTable(tables.Table):
    # put = tables.BooleanColumn(tables.utils.A("buyer__isnull"))
    put = tables.BooleanColumn(
        accessor=tables.utils.A("calculate_null"), orderable=False
    )
    
    class Meta:
        model = Option
        fields = ("lot", "start_time", "end_time", "price", "put")
