from django.contrib.auth.models import User
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver


class EOSAccount(models.Model):
    user = models.OneToOneField(User, related_name='a', on_delete=models.CASCADE)

    # TODO
    # 1) private_key TextField
    #    default should prob be a method that generates private key.
    #    Should later call eos api to create eos account in post_save
    #    for reference: https://stackoverflow.com/questions/16216363/how-can-you-store-a-rsa-key-pair-in-a-django-model-sqlite-db
    #
    # 2) possibly other fields including account and a second key
    #
    # Should add any new manually entered fields to REQUIRED_FIELDS

    # TODO find out precision and decide on default
    balance = models.DecimalField(default=1000.0, max_digits=20, decimal_places=10)
    minimum_balance = models.DecimalField(default=0.0, max_digits=20, decimal_places=10)


class Group(models.Model):
    name = models.CharField(max_length=50)
    creator = models.ForeignKey(EOSAccount, related_name='group_creator', on_delete=models.CASCADE)
    members = models.ManyToManyField(EOSAccount, related_name='members')
    Fee = models.DecimalField(max_digits=20, decimal_places=10)
    minimum_price = models.DecimalField(max_digits=20, decimal_places=10)
    minimum_ratio = models.DecimalField(max_digits=3, decimal_places=2)

    def __str__(self):
        return self.name


class Lot(models.Model):
    name = models.CharField(max_length=50)

    def __str__(self):
        return self.name


class Spot(models.Model):
    owner = models.ForeignKey(EOSAccount, on_delete=models.CASCADE)
    lot = models.ForeignKey(Lot, on_delete=models.CASCADE)
    number = models.IntegerField()
    group = models.ForeignKey(Group, null=True, blank=True, on_delete=models.CASCADE)
    # TODO
    # what should the owner default be if any?
    # is the naming scheme good?
    # should there be a price field?

    class Meta:
        unique_together = [['lot', 'number']]

    def __str__(self):
        return '{} | {}'.format(self.lot.name, self.number)

class Future(models.Model):
    creator = models.ForeignKey(EOSAccount, related_name='creator', on_delete=models.CASCADE)
    acceptor = models.ForeignKey(EOSAccount, related_name='acceptor', null=True, blank=True, on_delete=models.CASCADE)
    spot = models.ForeignKey(Spot, on_delete=models.CASCADE)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField(blank=True)
    request_expiration_time = models.DateTimeField()
    price = models.DecimalField(max_digits=20, decimal_places=10)
    is_purchase = models.BooleanField()


class Option(Future):
    fee = models.DecimalField(max_digits=20, decimal_places=10)
    collateral = models.DecimalField(max_digits=20, decimal_places=10)


@receiver(post_save, sender=User, dispatch_uid="create_user_eos_account")
def create_user_eos_account(sender, instance, created, **kwargs):
    if created:
        EOSAccount.objects.create(user=instance)
