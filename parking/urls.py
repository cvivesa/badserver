from django.urls import include, path
from django.views.generic.base import RedirectView

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("futures/calls", views.FutureCallList.as_view(), name="future_call_list"),
    path(
        "futures/calls/new", views.FutureCallCreate.as_view(), name="future_call_create"
    ),
    path("futures/puts", views.FuturePutList.as_view(), name="future_put_list"),
    path("futures/puts/new", views.FuturePutCreate.as_view(), name="future_put_create"),
    path("futures/transact/<int:pk>", views.future_transact, name="future_transact"),
    path("options/calls", views.OptionCallList.as_view(), name="option_call_list"),
    path(
        "options/calls/new", views.OptionCallCreate.as_view(), name="option_call_create"
    ),
    path("options/puts", views.OptionPutList.as_view(), name="option_put_list"),
    path("options/puts/new", views.OptionPutCreate.as_view(), name="option_put_create"),
    path("options/transact/<int:pk>", views.option_transact, name="option_transact"),
    path("spots/me", views.AccessibleSpotList.as_view(), name="accessible"),
    path("spots/me/pending", views.UserUnfullfilledFutureList.as_view(), name="pending"),
    path("spots/lookup", views.Whitepages.as_view(), name="whitepages"),
    path("groups/create", views.GroupCreate.as_view(), name="group_create"),
    path("groups/list", views.GroupList.as_view(), name="group_list"),
    path("", include("django.contrib.auth.urls")),
    path("signup", views.SignUp.as_view(), name="sign_up"),
]
