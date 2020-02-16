from django.contrib.auth.models import User
from django.core.management import BaseCommand

from parking.models import Future, Lot


class Command(BaseCommand):
    help = "Auctions off spots for use at the beginning of a semester"

    def handle(self, *args, **options):
        # assume "school" is first super user
        a = User.objects.filter(is_superuser=True).first().a

        for lot in Lot.objects.all():
            spots = list(lot.spots.all())
            futures = list(
                Future.objects.filter(lot=lot, seller__isnull=True).order_by("-price")
            )

            s_count = len(spots)
            f_count = len(futures)
            s_i = 0
            f_i = 0
            while s_i < s_count and f_i < f_count:
                s = spots[s_i]
                f = futures[f_i]
                if f.buyer.net_balance() >= f.price:
                    f.spot = s
                    f.seller = a
                    f.save()
                    f.buyer.balance -= f.price
                    f.buyer.save()
                    s_i += 1
                f_i += 1

        print("done")
