from django.urls import path

from . import views, magiclink_views

urlpatterns = [
    path("", views.IndexView.as_view(), name="index"),
    path("login/", magiclink_views.PhacOnlyLoginView.as_view(), name="phac_only_login"),
]
