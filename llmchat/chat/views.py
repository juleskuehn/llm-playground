from django.shortcuts import render
from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin

from magiclink.views import LoginVerify


class CustomLoginVerify(LoginVerify):
    pass


class IndexView(LoginRequiredMixin, TemplateView):
    template_name = "index.jinja"