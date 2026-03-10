from django.urls import path
from .views import UploadDatasetView

urlpatterns = [
    path("upload/<int:pk>/", UploadDatasetView.as_view(), name="upload-dataset"),
]