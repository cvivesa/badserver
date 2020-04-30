from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponseRedirect
from django.utils import timezone
from django.views.generic.edit import CreateView
from django_tables2 import SingleTableView
from django.forms.models import model_to_dict
import pytz

from .models import *
from .tables import *
from .filters import *

from common_interactions_eospy import *


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


@login_required
def profile(request):
    if request.method == "POST":
        future = get_object_or_404(Future, pk=request.POST["spot"])
        group = get_object_or_404(Group, pk=request.POST["group"])
        future.group = group
        future.save()
        # Future to a group future.group.pk
        ftrtogrp(owner, owner, future.grout.pk, future.pk, owner.private_key)
        return HttpResponseRedirect("profile")

    context = {
        "owned_groups": request.user.a.created_groups.all(),
        "allocated_spots": Future.objects.filter(
            buyer=request.user.a, seller__isnull=False, group__isnull=False
        ),
        "unallocated_spots": Future.objects.filter(
            buyer=request.user.a, seller__isnull=False, group__isnull=True
        ),
    }
    return render(request, "profile.html", context)


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
        # Creates a future half form.instance.fields
        create_future(
            form.instance.buyer,
            form.instance.buyer,
            "",
            form.instance.lot,
            "",
            form.instance.start_time,
            form.instance.end_time,
            form.instance.request_expiration_time,
            form.instance.price,
            future_id,
            form.instance.buyer.private_key,
        )
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
        # Creates a future half
        create_future(
            form.instance.seller,
            form.instance.seller,
            "",
            form.instance.lot,
            "",
            form.instance.start_time,
            form.instance.end_time,
            form.instance.request_expiration_time,
            form.instance.price,
            future_id,
            form.instance.seller.private_key,
        )
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
            seller=None, request_expiration_time__gte=timezone.now(),
        )


class FuturePutList(FutureCallList):
    template_name = "lists/future_put.html"

    def get_queryset(self):
        return Future.objects.filter(
            buyer=None, request_expiration_time__gte=timezone.now(),
        )


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
            .owned_by_self(a, f.start_time, f.end_time)
            .first()
        )
        if not s:
            return e("You didn't Have A Qualifying Spot")
        f.seller = a
        # Future complete
        complete_future(
            f.buyer,
            f.buyer,
            f.seller,
            f.lot.pk,
            s.spot,
            f.start_time,
            f.end_time,
            f.request_expiration_time,
            f.price,
            f.pk,
            f.buyer.private_key,
        )
    else:
        if a.net_balance() < f.price:
            return e("You didn't Have Enough Funds")
        s = (
            Future.objects.filter(lot=f.lot)
            .owned_by_self(f.seller, f.start_time, f.end_time)
            .first()
        )
        if not s:
            return e("The Seller didn't Have A Qualifying Spot")
        f.buyer = a
        # Future complete
        complete_future(
            f.seller,
            f.buyer,
            f.seller,
            f.lot.pk,
            s.spot,
            f.start_time,
            f.end_time,
            f.request_expiration_time,
            f.price,
            f.pk,
            f.seller.private_key,
        )

    f.spot = s.spot
    f.save()
    f.buyer.balance -= f.price
    f.buyer.save()
    f.seller.balance += f.price
    f.seller.save()

    remainder = (s.end_time - s.start_time).days
    # now modify s (the original future)
    if s.start_time < f.start_time:
        f1 = Future()
        f1.buyer = s.buyer
        f1.seller = s.seller
        f1.lot = s.lot
        f1.start_time = s.start_time
        f1.end_time = f.start_time
        f1.request_expiration_time = s.request_expiration_time
        f1.group = s.group
        # set the price to the day/price ratio
        f1.price = s.price * (f1.end_time - f1.start_time).days / remainder
        f1.spot = s.spot
        f1.save()
    elif s.end_time > f.end_time:
        f2 = Future()
        f2.buyer = s.buyer
        f2.seller = s.seller
        f2.lot = s.lot
        f2.start_time = f.end_time
        f2.end_time = s.end_time
        f2.request_expiration_time = s.request_expiration_time
        f2.group = s.group
        f2.price = s.price * (f2.end_time - f2.start_time).days / remainder
        f2.spot = s.spot
        f2.save()
    s.delete()
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
        form.instance.creator = self.request.user.a
        # creates an option half on the call side
        create_option(
            form.instance.creator,
            "",
            form.instance.buyer,
            form.instance.creator,
            "",
            form.instance.lot,
            form.instance.start_time,
            form.instance.end_time,
            form.instance.request_expiration_time,
            form.instance.request_expiration_time,
            form.instance.price,
            form.instance.fee,
            form.instance.collateral,
            form.instance.creator.private_key,
        )
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
        form.instance.creator = self.request.user.a
        # creates an option half on the put side
        create_option(
            form.instance.creator,
            "",
            form.instance.seller,
            "",
            form.instance.creator,
            form.instance.lot,
            form.instance.start_time,
            form.instance.end_time,
            form.instance.request_expiration_time,
            form.instance.request_expiration_time,
            form.instance.price,
            form.instance.fee,
            form.instance.collateral,
            form.instance.creator.private_key,
        )
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


class AcceptedOptionList(FilteredSingleTableView):
    table_class = AcceptedOptionTable
    template_name = "lists/base.html"
    filter_class = AcceptedOptionFilter

    def get_queryset(self):
        return Option.objects.filter(
            (Q(buyer=self.request.user.a) | Q(seller=self.request.user.a)),
            buyer__isnull=False,
            seller__isnull=False,
            end_time__gte=timezone.now(),
        ).exclude(creator=self.request.user.a)


@login_required
def option_transact(request, pk):
    # TODO consider groups
    # TODO should delete on failure
    e = lambda msg: render(request, "error.html", {"msg": msg})
    f = get_object_or_404(Option, pk=pk)
    # a is NOT the creator
    a = request.user.a

    if timezone.now() > f.request_expiration_time:
        return e("The Option is Expired")
    if f.buyer == a or f.seller == a:
        return e("You can't Accept Your Own Option")
    if f.buyer and f.seller:
        return e("The Option was Already Accepted")

    """if a.net_balance() < f.collateral:
            return e("You did not have enough funds to cover the collateral")"""
    # call
    if f.seller == None:
        if f.buyer.net_balance() < f.fee:
            return e("The Buyer didn't Have Enough Funds")

        s = (
            Future.objects.filter(lot=f.lot)
            .owned_by_self(a, f.start_time, f.end_time)
            .first()
        )
        if not s:
            return e("You didn't Have A Qualifying Spot")
        f.seller = a
        f.seller.balance -= f.fee
        f.seller.save()
        f.buyer.save()
        f.buyer.balance += f.fee
        f.buyer.save()
        complete_option(
            f.buyer,
            f.buyer,
            f.seller,
            f.buyer,
            f.seller,
            f.lot,
            f.start_time,
            f.end_time,
            f.request_expiration_time,
            f.request_expiration_time,
            f.price,
            f.fee,
            f.collateral,
            f.pk,
            f.buyer.private_key,
        )
    # put
    else:
        if a.net_balance() < f.fee:
            return e("You didn't Have Enough Funds  to cover the fee")
        s = (
            Future.objects.filter(lot=f.lot)
            .owned_by_self(f.seller, f.start_time, f.end_time)
            .first()
        )
        if not s:
            return e("The Seller didn't Have A Qualifying Spot")
        f.buyer = a
        f.buyer.balance -= f.fee
        f.buyer.save()
        f.seller.balance += f.fee
        f.seller.save()
        complete_option(
            f.seller,
            f.seller,
            f.buyer,
            f.buyer,
            f.seller,
            f.lot,
            f.start_time,
            f.end_time,
            f.request_expiration_time,
            f.request_expiration_time,
            f.price,
            f.fee,
            f.collateral,
            f.pk,
            f.seller.private_key,
        )

    f.spot = s.spot
    # Completes the other half of an option
    f.save()

    return redirect("index")


@login_required
def option_exercise(request, pk):
    e = lambda msg: render(request, "error.html", {"msg": msg})
    o = get_object_or_404(Option, pk=pk)
    # a is NOT the creator
    a = request.user.a
    # case for put
    # Option exercise, either exercise put or call
    if o.creator == o.seller:
        if a.net_balance() < o.price:
            return e("You do not have enough to pay to exercise the option")
        exrcall(o.creator, o.creator, o.seller, o.pk, o.seller.private_key)
    # case for call
    if o.creator == o.seller:
        if o.seller.balance < o.price:
            o.creator.balance -= o.collateral
            a.balance += o.collateral
            o.delete()
            exrcall(o.creator, o.creator, o.seller, o.pk, o.creator.private_key)
    f = Future()

    f.buyer = o.buyer
    f.seller = o.seller
    f.lot = o.lot
    f.start_time = o.start_time
    f.end_time = o.end_time
    f.request_expiration_time = o.request_expiration_time
    f.group = o.group
    f.price = o.price
    o.delete()
    s = (
        Future.objects.filter(lot=f.lot)
        .owned_by_self(f.seller, f.start_time, f.end_time)
        .first()
    )
    if not s:
        o.creator.balance -= o.collateral
        a.balance += o.collateral
        o.delete()
        f.delete()
        return e(
            "The seller did not have the future, you will be compensated in collateral"
        )

    f.spot = s.spot
    f.save()
    f.buyer.balance -= f.price
    f.buyer.save()
    f.seller.balance += f.price
    f.seller.save()
    # now modify s (the original future)
    if s.start_time == f.start_time and s.end_time == f.end_time:
        s.delete()
        return redirect("index")
    remainder = (s.end_time - s.start_time).days
    if s.start_time < f.start_time:
        f1 = Future()
        f1.buyer = s.buyer
        f1.seller = s.seller
        f1.lot = s.lot
        f1.start_time = s.start_time
        f1.end_time = f.start_time
        f1.request_expiration_time = s.request_expiration_time
        f1.group = s.group
        f1.price = s.price * (f1.end_time - f1.start_time).days / remainder
        f1.spot = s.spot
        f1.save()
    if s.end_time > f.end_time:
        f2 = Future()
        f2.buyer = s.buyer
        f2.seller = s.seller
        f2.lot = s.lot
        f2.start_time = f.end_time
        f2.end_time = s.end_time
        f2.request_expiration_time = s.request_expiration_time
        f2.group = s.group
        f2.price = s.price * (f2.end_time - f2.start_time).days / remainder
        f2.spot = s.spot
        f2.save()

    s.delete()
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
        )


class UserUnfullfilledOptionList(FutureCallList):
    template_name = "lists/base.html"
    table_class = UnfullFilledOptionTable

    def get_queryset(self):
        return Option.objects.filter(
            (Q(buyer__isnull=True) | Q(seller__isnull=True)),
            creator=self.request.user.a,
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
        # Create Group
        crtgroup(
            form.instance.creator,
            "title",
            form.instance.creator,
            form.instance.fee,
            form.instance.min_ratio,
            "",
            form.instance.creator.private_key,
        )
        return super().form_valid(form)

    def get_success_url(self):
        print(vars(self.object))
        return "/"


class GroupList(FilteredSingleTableView):
    table_class = GroupTable
    template_name = "lists/base.html"
    filter_class = GroupFilter

    def get_queryset(self):
        return Group.objects.exclude(creator=self.request.user.a).exclude(
            id__in=self.request.user.a.joined_groups.all()
        )


@login_required
def group_join(request, pk):
    e = lambda msg: render(request, "error.html", {"msg": msg})
    g = get_object_or_404(Group, pk=pk)
    a = request.user.a

    if g.creator == a:
        return e("You're Automatically In Your Own Group")
    if a.net_balance() < g.fee:
        return e("You Don't Have Enough (Un-Reserved) Funds")

    a.balance -= g.fee
    a.save()
    g.creator.balance += g.fee
    g.creator.save()
    # Join a group
    joingroup(a, a, g.pk, a.private_key)
    g.members.add(a)
    return redirect("index")


class SignUp(CreateView):
    form_class = UserCreationForm
    success_url = "/"
    template_name = "registration/signup.html"
