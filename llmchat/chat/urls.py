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
    path("summary/<int:doc_id>", views.summary, name="summary"),
    path("full_text/<int:doc_id>", views.full_text, name="full_text"),
    path("embeddings/<int:doc_id>", views.generate_embeddings, name="embeddings"),
    path("query_embeddings", views.query_embeddings, name="query_embeddings"),
    path("qa_embeddings", views.qa_embeddings, name="qa_embeddings"),
    path("chat_settings", views.chat_settings, name="chat_settings"),
    path("_ah/warmup", views.warmup, name="warmup"),
]
