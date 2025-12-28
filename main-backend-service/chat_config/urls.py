from django.urls import path
from .views import ChatListCreateView, ChatDetailView, GenerateChatNameView, UpdateChatNameView

urlpatterns = [
    path("chat-list-create/", ChatListCreateView.as_view(), name="chat-list-create"),
    path("chat-detail/<int:pk>/", ChatDetailView.as_view(), name="chat-detail"),
    path("chat-generate-name/<int:pk>/", GenerateChatNameView.as_view(), name="chat-generate-name"),
    path("chat-update-name/<int:pk>/", UpdateChatNameView.as_view(), name="chat-update-name"),
]
