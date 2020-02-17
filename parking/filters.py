from django_filters import rest_framework as filters

from .models import Future


class FutureFilter(filters.FilterSet):
    class Meta:
        model = Future
        fields = {
            "lot": ["exact"],
            "start_time": ["lte"],
            "end_time": ["gte"],
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for _, f in self.filters.items():
            f.field.widget.attrs.update({'class': 'input'})
