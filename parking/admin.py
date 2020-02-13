from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User

from .models import EOSAccount, Lot, Spot, Group, Future, Option

class EOSAccountInline(admin.StackedInline):
    model = EOSAccount
    can_delete = False
    verbose_name_plural = 'EOS Account'


class UserAdmin(BaseUserAdmin):
    inlines = (EOSAccountInline,)

admin.site.unregister(User)
admin.site.register(User, UserAdmin)

admin.site.register(Lot)
admin.site.register(Spot)
admin.site.register(Group)
admin.site.register(Future)
admin.site.register(Option)