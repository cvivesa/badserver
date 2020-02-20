from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render, get_object_or_404, redirect
from django.utils import timezone
from django.views.generic.edit import CreateView
from django_tables2 import SingleTableView
import pytz

from .models import Spot, Future
from .tables import FutureTable, AcceptedFutureTable
from .forms import FutureCallForm, FuturePutForm
from .filters import FutureFilter, SingleUserSpotFilter, MultipleUserSpotFilter


class FilteredSingleTableView(LoginRequiredMixin, SingleTableView):
    filter_class = None

    def get_table_data(self):
        data = self.get_queryset()
        self.filter = self.filter_class(
            self.request.GET, queryset=data, a=self.request.user.a
        )
        return self.filter.qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["filter"] = self.filter
        return context


@login_required
def index(request):
    return render(request, "index.html", {})


class FutureCallCreate(LoginRequiredMixin, CreateView):
    model = Future
    form_class = FutureCallForm
    template_name = "create_form.html"

    def form_valid(self, form):
        form.instance.buyer = self.request.user.a
        return super().form_valid(form)

    def get_success_url(self):
        print(vars(self.object))
        return "/"


class FuturePutCreate(LoginRequiredMixin, CreateView):
    model = Future
    form_class = FuturePutForm
    template_name = "create_form.html"

    def form_valid(self, form):
        form.instance.seller = self.request.user.a
        return super().form_valid(form)

    def get_success_url(self):
        print(vars(self.object))
        return "/"


class FutureCallList(FilteredSingleTableView):
    table_class = FutureTable
    template_name = "lists/future_call.html"
    filter_class = FutureFilter

    def get_queryset(self):
        return Future.objects.filter(
            seller=None,
            request_expiration_time__gte=timezone.now(),
            # TODO spot__in=self.request.user.a.owned_spots.all(),
        )


# TODO need special view to accept to specify group
class FuturePutList(FutureCallList):
    template_name = "lists/future_put.html"

    def get_queryset(self):
        # TODO is the exclude feasible?
        return Future.objects.filter(
            buyer=None, request_expiration_time__gte=timezone.now(),
        )  # .exclude(spot__in=self.request.user.a.owned_spots.all())


@login_required
def future_transact(request, pk):
    # TODO should delete on failure
    e = lambda msg: render(request, "error.html", {"msg": msg})
    f = get_object_or_404(Future, pk=pk)
    a = request.user.a

    if timezone.now() > f.request_expiration_time:
        return e("The Future is Expired")
    if f.buyer == a or f.seller == a:
        return e("You can't Accept Your Own Future")
    if f.buyer and f.seller:
        return e("The Future was Already Accepted")

    if f.seller == None:
        if f.buyer.net_balance() < f.price:
            return e("The Buyer didn't Have Enough Funds")
        s = (
            Future.objects.filter(lot=f.lot)
            .owned_by(a, f.start_time, f.end_time)
            .first()
        )
        if not s:
            return e("You didn't Have A Qualifying Spot")
        f.seller = a
    else:
        if a.net_balance() < f.price:
            return e("You didn't Have Enough Funds")
        s = (
            Future.objects.filter(lot=f.lot)
            .owned_by(f.seller, f.start_time, f.end_time)
            .first()
        )
        if not s:
            return e("The Seller didn't Have A Qualifying Spot")
        f.buyer = a

    f.spot = s
    f.save()
    f.buyer.balance -= f.price
    f.buyer.save()
    f.seller.balance += f.price
    f.seller.save()
    return redirect("index")


class AccessibleSpotList(FilteredSingleTableView):
    table_class = AcceptedFutureTable
    template_name = "lists/base.html"
    filter_class = SingleUserSpotFilter
    model = Future


class Whitepages(AccessibleSpotList):
    filter_class = MultipleUserSpotFilter


class SignUp(CreateView):
    form_class = UserCreationForm
    success_url = "/"
    template_name = "registration/signup.html"
