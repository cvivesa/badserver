import django_tables2 as tables

from .models import Future

class FutureTable(tables.Table):
    class Meta:
        model = Future