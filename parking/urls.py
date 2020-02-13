from django.urls import include, path
from django.views.generic.base import RedirectView

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('futures/new', views.FutureCreate.as_view(), name='future_create'),
    path('futures', views.FutureList.as_view(), name='future_list'),
    path('', include('django.contrib.auth.urls')),
]

