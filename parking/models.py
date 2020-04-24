from django.contrib.auth.models import User
from django.db import models
from django.db.models import Q, Sum
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.urls import reverse
from django.utils import timezone


class EOSAccount(models.Model):
    user = models.OneToOneField(User, related_name="a", on_delete=models.CASCADE)

    # TODO
    # 1) private_key TextField
    #    default should prob be a method that generates private key.
    #    Should later call eos api to create eos account in post_save
    #    for reference: https://stackoverflow.com/questions/16216363/how-can-you-store-a-rsa-key-pair-in-a-django-model-sqlite-db
    #
    # 2) possibly other fields including account and a second key
    #
    # Should add any new manually entered fields to REQUIRED_FIELDS

    #  find out precision and decide on default
    balance = models.DecimalField(default=1000.0, max_digits=10, decimal_places=2)

    def __str__(self):
        return str(self.user)

    def net_balance(self):
        t = timezone.now()
        options = Option.objects.filter(end_time__gt=t).filter(
            (Q(seller=self) & Q(buyer__isnull=False))
            | (Q(buyer=self) & Q(seller__isnull=False)),
            creator=self,
        )
        s = options.aggregate(Sum("collateral")).get("collateral__sum", 0)
        if s:
            return self.balance - s
        return self.balance

    def collateral(self):
        return self.balance - self.net_balance()

    def owns(self, spot, start, end):
        return Future.objects.filter(spot=spot).owned_by_self(self, start, end).exists()

    def owns(self, start, end):
        return Future.objects.owned_by_self(self, start, end).values_list("spot", flat=True)


class Group(models.Model):
    name = models.CharField(max_length=50)
    creator = models.ForeignKey(
        EOSAccount, related_name="created_groups", on_delete=models.CASCADE
    )
    members = models.ManyToManyField(
        EOSAccount, blank=True, related_name="joined_groups"
    )
    fee = models.DecimalField(max_digits=10, decimal_places=2)
    minimum_price = models.DecimalField(max_digits=10, decimal_places=2)
    minimum_ratio = models.DecimalField(max_digits=3, decimal_places=2)

    def __str__(self):
        return self.name

    def futures(self):
        return Future.objects.filter(group=self, seller__isnull=False)


class Lot(models.Model):
    name = models.CharField(max_length=50)

    def __str__(self):
        return self.name


class Spot(models.Model):
    lot = models.ForeignKey(Lot, related_name="spots", on_delete=models.CASCADE)
    number = models.IntegerField()

    class Meta:
        unique_together = [["lot", "number"]]

    def __str__(self):
        return "{} | {}".format(self.lot.name, self.number)


# TODO: note this wont account for any of:
#  two back-to-back purchases that combined cover the range
#  selling a spot and buying it back
class FutureQuerySet(models.QuerySet):
    def owned_by_self(self, a, start, end):
        return self.filter(
            start_time__lte=start, end_time__gte=end, buyer=a, seller__isnull=False,
        )

    def owned_by_groups(self, a, start, end):
        groups = a.joined_groups.all()
        owners = groups.values_list("creator", flat=True)

        return self.filter(
            start_time__lte=start,
            end_time__gte=end,
            group__in=groups,
            seller__isnull=False,
            buyer__isnull=False,
        )

    def accessible(self, a, start, end):
        return queryset.owned_by_self(a, start, end).union(
            queryset.owned_by_groups(a, start, end)
        )


class Future(models.Model):
    buyer = models.ForeignKey(
        EOSAccount, related_name="+", null=True, blank=True, on_delete=models.CASCADE
    )
    seller = models.ForeignKey(
        EOSAccount, related_name="+", null=True, blank=True, on_delete=models.CASCADE
    )
    lot = models.ForeignKey(Lot, on_delete=models.CASCADE)
    spot = models.ForeignKey(Spot, null=True, blank=True, on_delete=models.CASCADE)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField(blank=True)
    request_expiration_time = models.DateTimeField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    group = models.ForeignKey(
        Group, related_name="+", null=True, blank=True, on_delete=models.CASCADE
    )

    objects = FutureQuerySet.as_manager()

    def get_absolute_url(self):
        # TODO account for different link for purchases to specify group
        return reverse("future_transact", args=[self.pk])


class Option(models.Model):
    buyer = models.ForeignKey(
        EOSAccount, related_name="+", null=True, blank=True, on_delete=models.CASCADE
    )
    seller = models.ForeignKey(
        EOSAccount, related_name="+", null=True, blank=True, on_delete=models.CASCADE
    )
    lot = models.ForeignKey(Lot, on_delete=models.CASCADE)
    spot = models.ForeignKey(Spot, null=True, blank=True, on_delete=models.CASCADE)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField(blank=True)
    request_expiration_time = models.DateTimeField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    group = models.ForeignKey(
        Group, related_name="+", null=True, blank=True, on_delete=models.CASCADE
    )
    fee = models.DecimalField(max_digits=10, decimal_places=2)
    collateral = models.DecimalField(max_digits=10, decimal_places=2)
    creator = models.ForeignKey(
        EOSAccount, related_name="+", null=True, blank=True, on_delete=models.CASCADE
    )
    # option is valid until Future.request_expiration_time

    def get_absolute_url(self):
        if self.buyer and self.seller:
            return reverse("option_exercise", args=[self.pk])
        return reverse("option_transact", args=[self.pk])

    def calculate_null(self):
        return not self.buyer

    def calculate_put(self):
        return self.creator == self.seller



@receiver(post_save, sender=User, dispatch_uid="create_user_eos_account")
def create_user_eos_account(sender, instance, created, **kwargs):
    if created:
        EOSAccount.objects.create(user=instance)
