from django.urls import path
from .views import GenerateCodeView, ModelListView

urlpatterns = [
    path("generate/", GenerateCodeView.as_view(), name="generate_code"),
    path("models/", ModelListView.as_view(), name="list_models"),
]