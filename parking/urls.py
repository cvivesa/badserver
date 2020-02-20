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
    path("spots/me", views.AccessibleSpotList.as_view(), name="accessible"),
    path("spots/lookup", views.Whitepages.as_view(), name="whitepages"),
    path("", include("django.contrib.auth.urls")),
    path("signup", views.SignUp.as_view(), name="sign_up"),
]
