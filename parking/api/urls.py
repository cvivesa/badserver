from django.urls import path
from . import views


urlpatterns = [
    path("futures/", views.FutureAPIView.as_view(), name="future_history"),
]
