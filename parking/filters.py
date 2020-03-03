from django_filters import rest_framework as filters

from .models import Future, EOSAccount, Option


class FutureFilter(filters.FilterSet):
    class Meta:
        model = Future
        fields = {
            "lot": ["exact"],
            "start_time": ["lte"],
            "end_time": ["gte"],
        }

    def __init__(self, *args, **kwargs):
        del kwargs["a"]
        super().__init__(*args, **kwargs)
        for _, f in self.filters.items():
            f.field.widget.attrs.update({"class": "input"})


class OptionFilter(FutureFilter):
    class Meta(FutureFilter.Meta):
        model = Option
        fields = {
            "lot": ["exact"],
            "start_time": ["lte"],
            "end_time": ["gte"],
            "request_expiration_time": ["lte"],
            "fee": ["gte"],
            "collateral": ["gte"],
        }


class SingleUserSpotFilter(filters.FilterSet):
    date_range = filters.DateTimeFromToRangeFilter(label="Date Range")

    class Meta:
        model = Future
        fields = ["lot", "date_range"]

    def __init__(self, *args, **kwargs):
        self.a = kwargs.pop("a", None)
        super().__init__(*args, **kwargs)
        for _, f in self.filters.items():
            f.field.widget.attrs.update({"class": "input"})

    def filter_queryset(self, queryset):
        dates = self.form.cleaned_data.get("date_range", None)
        if dates:
            return queryset.owned_by(self.a, dates.start, dates.stop).union(
                queryset.owned_by_groups(self.a, dates.start, dates.stop)
            )
        return Future.objects.none()


class MultipleUserSpotFilter(filters.FilterSet):
    user = filters.ModelChoiceFilter(label="User", queryset=EOSAccount.objects.all())
    date_range = filters.DateTimeFromToRangeFilter(label="Date Range")

    def __init__(self, *args, **kwargs):
        self.a = kwargs.pop("a", None)
        super().__init__(*args, **kwargs)
        for _, f in self.filters.items():
            f.field.widget.attrs.update({"class": "input"})

    def filter_queryset(self, queryset):
        a = self.form.cleaned_data.get("user", None)
        dates = self.form.cleaned_data.get("date_range", None)
        if a and dates:
            return queryset.owned_by(a, dates.start, dates.stop).union(
                queryset.owned_by_groups(a, dates.start, dates.stop)
            )
        return Future.objects.none()
