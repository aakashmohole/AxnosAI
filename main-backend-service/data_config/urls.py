from django.urls import path
from .views import UploadDatasetView, UploadDatasetToChatView

urlpatterns = [
    path("upload-dataset/", UploadDatasetView.as_view(), name="dataset-upload"),
    path("upload-update-dataset/<int:pk>/", UploadDatasetToChatView.as_view(), name="dataset-upload-update-chat"),
]
