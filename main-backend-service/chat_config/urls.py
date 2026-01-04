from django.urls import path
from .views import CreateChatWithDatasetView, ChatDetailView, GenerateChatNameView, ListUserChatsView, UpdateChatNameView, FetchTablePreviewAPIView

urlpatterns = [
    path("chat-list-create/", CreateChatWithDatasetView.as_view(), name="chat-list-create"),
    path("chat-detail/<int:pk>/", ChatDetailView.as_view(), name="chat-detail"),
    path("chat-generate-name/<int:pk>/", GenerateChatNameView.as_view(), name="chat-generate-name"),
    path("chat-update-name/<int:pk>/", UpdateChatNameView.as_view(), name="chat-update-name"),
    path("fetch-table-records/", FetchTablePreviewAPIView.as_view(), name="fetch-table-records"),

    # fetch all chats of a user
    path("user-chats/", ListUserChatsView.as_view(), name="user-chats"),
]
