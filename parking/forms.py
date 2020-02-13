from django import forms


from .models import Future


class FutureForm(forms.ModelForm):
    class Meta:
        model = Future
        fields = ['spot', 'start_time', 'end_time', 'request_expiration_time', 'price', 'is_purchase']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for _, f in self.fields.items():
            f.widget.attrs.update({'class': 'input'})
