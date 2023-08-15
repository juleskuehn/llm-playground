from django.urls import path

from . import views, magiclink_views

urlpatterns = [
    path("", views.NewChatView.as_view(), name="index"),
    path("login/", magiclink_views.PhacOnlyLoginView.as_view(), name="phac_only_login"),
    path("logout/", views.logout_view, name="logout"),
    path("chat/<int:chat_id>", views.ChatView.as_view(), name="chat"),
    path("chat/chat_response/<int:chat_id>", views.chat_response, name="chat_response"),
    path("chat/delete/<int:chat_id>/<str:current_chat>", views.delete_chat, name="delete_chat"),
    path("documents/", views.DocumentsView.as_view(), name="documents"),
]
