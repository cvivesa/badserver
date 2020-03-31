from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render, get_object_or_404, redirect
from django.utils import timezone
from django.views.generic.edit import CreateView
from django_tables2 import SingleTableView
import pytz

from .models import *
from .tables import *
from .filters import *


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
    fields = [
        "lot",
        "start_time",
        "end_time",
        "request_expiration_time",
        "price",
        "group",
    ]
    template_name = "create_form.html"

    def form_valid(self, form):
        form.instance.buyer = self.request.user.a
        return super().form_valid(form)

    def get_success_url(self):
        print(vars(self.object))
        return "/"


class FuturePutCreate(LoginRequiredMixin, CreateView):
    model = Future
    fields = ["lot", "start_time", "end_time", "request_expiration_time", "price"]
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
    # TODO consider groups
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


class OptionCallCreate(LoginRequiredMixin, CreateView):
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
    template_name = "create_form.html"

    def form_valid(self, form):
        form.instance.buyer = self.request.user.a
        return super().form_valid(form)

    def get_success_url(self):
        print(vars(self.object))
        return "/"


class OptionPutCreate(LoginRequiredMixin, CreateView):
    model = Option
    fields = [
        "lot",
        "start_time",
        "end_time",
        "request_expiration_time",
        "price",
        "fee",
        "collateral",
    ]
    template_name = "create_form.html"

    def form_valid(self, form):
        form.instance.seller = self.request.user.a
        return super().form_valid(form)

    def get_success_url(self):
        print(vars(self.object))
        return "/"


class OptionCallList(FilteredSingleTableView):
    table_class = OptionTable
    template_name = "lists/option_call.html"
    filter_class = OptionFilter

    def get_queryset(self):
        return Option.objects.filter(
            seller=None,
            request_expiration_time__gte=timezone.now(),
            # TODO spot__in=self.request.user.a.owned_spots.all(),
        )


# TODO need special view to accept to specify group
class OptionPutList(OptionCallList):
    template_name = "lists/option_put.html"

    def get_queryset(self):
        # TODO is the exclude feasible?
        return Option.objects.filter(
            buyer=None, request_expiration_time__gte=timezone.now(),
        )  # .exclude(spot__in=self.request.user.a.owned_spots.all())


@login_required
def option_transact(request, pk):
    return redirect("index")

    # TODO consider groups



    # change all references of Future to Option
    # TODO should delete on failure
    e = lambda msg: render(request, "error.html", {"msg": msg})
    f = get_object_or_404(Option, pk=pk)
    a = request.user.a

    if timezone.now() > f.request_expiration_time:
        return e("The Option is Expired")
    if f.buyer == a or f.seller == a:
        return e("You can't Accept Your Own Option")
    if f.buyer and f.seller:
        return e("The Option was Already Accepted")

    if f.seller == None:
        if f.buyer.net_balance() < f.price:
            return e("The Buyer didn't Have Enough Funds or there was not enough to cover the colateral")
        s = (
            Option.objects.filter(lot=f.lot)
            .owned_by(a, f.start_time, f.end_time)
            .first()
        )
        if not s:
            return e("You didn't Have A Qualifying Spot")
        f.seller = a
    else:
        if a.net_balance() < f.price:
            return e("You didn't Have Enough Funds or there was not enough to cover the colateral")
        s = (
            Option.objects.filter(lot=f.lot)
            .owned_by(f.seller, f.start_time, f.end_time)
            .first()
        )
        if not s:
            return e("The Seller didn't Have A Qualifying Spot")
        f.buyer = a

    f.spot = s
    f.save()
    f.buyer.balaFuturence -= f.price
    f.buyer.save()
    f.seller.balance += f.price
    f.seller.save()
    # remember to actually create the corresponding future
    return redirect("index")



class AccessibleSpotList(FilteredSingleTableView):
    table_class = AcceptedFutureTable
    template_name = "lists/single_user_accessible.html"
    filter_class = SingleUserSpotFilter
    model = Future


class UserUnfullfilledFutureList(FutureCallList):
    template_name = "lists/base.html"

    def get_queryset(self):
        return Future.objects.filter(
            seller=None,
            buyer=self.request.user.a,
            request_expiration_time__gte=timezone.now(),
            # TODO spot__in=self.request.user.a.owned_spots.all(),
        )


class Whitepages(AccessibleSpotList):
    template_name = "lists/base.html"
    filter_class = MultipleUserSpotFilter


class GroupCreate(LoginRequiredMixin, CreateView):
    model = Group
    fields = ["name", "fee", "minimum_price", "minimum_ratio"]
    template_name = "create_form.html"

    def form_valid(self, form):
        form.instance.creator = self.request.user.a
        return super().form_valid(form)

    def get_success_url(self):
        print(vars(self.object))
        return "/"


class GroupList(FilteredSingleTableView):
    table_class = GroupTable
    template_name = "lists/base.html"
    filter_class = GroupFilter

    def get_queryset(self):
        return Group.objects.exclude(creator=self.request.user.a)


@login_required
def group_join(request, pk):
    e = lambda msg: render(request, "error.html", {"msg": msg})
    g = get_object_or_404(Group, pk=pk)
    a = request.user.a

    # TODO a person joining a group could make the minimums fail

    if g.owner == a:
        return e("You're Automatically In Your Own Group")
    if a.net_balance() < g.fee:
        return e("You Don't Have Enough (Un-Reserved) Funds")
    # TODO Handle Ratios

    a.balance -= g.fee
    a.save()
    g.owner.balance += g.fee
    g.owner.save()

    g.members.add(a)
    return redirect("index")


class SignUp(CreateView):
    form_class = UserCreationForm
    success_url = "/"
    template_name = "registration/signup.html"
