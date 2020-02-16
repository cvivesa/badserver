from django import forms

from .models import Future


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
