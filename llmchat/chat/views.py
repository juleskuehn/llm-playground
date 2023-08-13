from django.shortcuts import render, redirect
from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth import logout

from chat.forms import MessageForm
from chat.models import Message, User, Chat


class IndexView(LoginRequiredMixin, TemplateView):
    template_name = "index.jinja"


class ChatView(LoginRequiredMixin, TemplateView):
    # Add a form to the context
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["chat"] = Chat.objects.get(id=kwargs["chat_id"])
        context["form"] = MessageForm()
        return context
    
    def post(self, request, *args, **kwargs):
        form = MessageForm(request.POST)
        if form.is_valid():
            message = Message.objects.create(
                message=form.cleaned_data["message"],
                chat_id=kwargs["chat_id"],
            )
            messages = Message.objects.filter(chat_id=kwargs["chat_id"])
            return render(request, "fragments/messages.jinja", {"messages": messages})
        else:
            return self.render_to_response({"form": form})

    template_name = "chat.jinja"


class NewChatView(ChatView):
    """
    Creates a new chat on GET and renders the chat template
    """
    def get(self, request, *args, **kwargs):
        # Create a new chat
        chat = Chat.objects.create(user=request.user)
        # Redirect to the chat view
        return redirect("chat", chat_id=chat.id)


class SingleMessageView(LoginRequiredMixin, TemplateView):
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["message"] = Message.objects.get(id=kwargs["message_id"])
        return context

    def post(self, request, *args, **kwargs):
        form = MessageForm(request.POST)
        if form.is_valid():
            message = Message.objects.create(
                author=request.user,
                message=form.cleaned_data["message"],
                chat_id=kwargs["chat_id"],
            )
            return render(request, "single_message.jinja", {"message": message})
        else:
            return self.render_to_response({"form": form})

    template_name = "single_message.jinja"


def logout_view(request):
    logout(request)
    return redirect("index")
