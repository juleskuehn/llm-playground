from django.shortcuts import render, redirect
from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth import logout

from langchain.chat_models import ChatVertexAI
from langchain.llms import VertexAI
from langchain.schema import HumanMessage, SystemMessage, AIMessage

chat_llm = ChatVertexAI(max_output_tokens=1024)
text_llm = VertexAI()

from chat.forms import MessageForm
from chat.models import Message, User, Chat


class IndexView(LoginRequiredMixin, TemplateView):
    template_name = "index.jinja"


def chat_response(request, chat_id):
    messages = Message.objects.filter(chat_id=chat_id)
    chat_messages = [
        SystemMessage(
            content="You are a helpful general purpose AI. You respond to user queries correctly and harmlessly. You always reason step by step to ensure you get the correct answer, and ask for clarification when you need it.",
        )
    ]
    for message in messages:
        if message.is_bot:
            chat_messages.append(AIMessage(content=message.message))
        else:
            chat_messages.append(HumanMessage(content=message.message))
    bot_message = Message.objects.create(
        message=chat_llm(chat_messages).content,
        chat_id=chat_id,
        is_bot=True,
    )
    return render(request, "fragments/waiting_message.jinja", {"message": bot_message})


class ChatView(LoginRequiredMixin, TemplateView):
    # GET method returns the entire chat page
    # POST method creates message
    # and returns HTML fragment with message + "LLM typing" indicator
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["chat"] = Chat.objects.get(id=kwargs["chat_id"])
        context["form"] = MessageForm()
        # Get non-empty chats for user
        user_chats = Chat.objects.filter(user=self.request.user).order_by("-timestamp")
        user_chats = [chat for chat in user_chats if chat.message_set.count() > 1]
        # Summarize chats into chat.title if not already set
        for chat in user_chats:
            if chat.title == "":
                chat.title = summarize_chat(chat.id)
                chat.save()
        context["user_chats"] = user_chats
        return context

    def post(self, request, *args, **kwargs):
        form = MessageForm(request.POST)
        if form.is_valid():
            user_message = Message.objects.create(
                message=form.cleaned_data["message"],
                chat_id=kwargs["chat_id"],
            )
            return render(
                request,
                "fragments/waiting_message.jinja",
                {
                    "message": user_message,
                    "chat_id": kwargs["chat_id"],
                    "waiting": True,
                },
            )
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


def logout_view(request):
    logout(request)
    return redirect("index")


def summarize_chat(chat_id):
    chat_text = "\n".join(
        [message.message for message in Message.objects.filter(chat_id=chat_id)[:5]]
    )
    if chat_text == "":
        return "Empty chat"
    if len(chat_text) > 500:
        chat_text = chat_text[:500]
    prompt = f"""
    Write a concise title (1-4 words) to the following chat. You must respond with at least one word:
    {chat_text}
    TITLE: """
    return text_llm(prompt)
