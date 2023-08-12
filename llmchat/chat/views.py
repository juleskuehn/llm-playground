from django.shortcuts import render, redirect
from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth import logout

from chat.forms import MessageForm

class IndexView(LoginRequiredMixin, TemplateView):
    # template_name = "index.jinja"
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["form"] = MessageForm()
        return context
    
    template_name = "chat.jinja"


class ChatView(LoginRequiredMixin, TemplateView):
    # Add a form to the context
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["form"] = MessageForm()
        return context
    
    template_name = "chat.jinja"


def logout_view(request):
    logout(request)
    return redirect("index")