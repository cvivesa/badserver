from django.urls import path
from . import views


urlpatterns = [
    path("futures/", views.FutureAPIView.as_view(), name="future_history"),
    path("futures/<int:pk>", views.FutureAPIView.as_view(), name="future_history"),
    path("options/", views.OptionAPIView.as_view(), name="option_history"),
    path("options/<int:pk>", views.OptionAPIView.as_view(), name="option_history"),
]
