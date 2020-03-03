from django import forms

from .models import Future, Option


class FutureCallForm(forms.ModelForm):
    class Meta:
        model = Future
        fields = [
            "lot",
            "start_time",
            "end_time",
            "request_expiration_time",
            "price",
            "group",
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for _, f in self.fields.items():
            f.widget.attrs.update({"class": "input"})


class FuturePutForm(FutureCallForm):
    class Meta(FutureCallForm.Meta):
        fields = ["lot", "start_time", "end_time", "request_expiration_time", "price"]


class OptionCallForm(forms.ModelForm):
    class Meta:
        model = Option
        fields = [
            "lot",
            "start_time",
            "end_time",
            "request_expiration_time",
            "price",
            "group",
            "fee",
            "collateral",
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for _, f in self.fields.items():
            f.widget.attrs.update({"class": "input"})


class OptionPutForm(OptionCallForm):
    class Meta(OptionCallForm.Meta):
        fields = [
            "lot",
            "start_time",
            "end_time",
            "request_expiration_time",
            "price",
            "fee",
            "collateral",
        ]
