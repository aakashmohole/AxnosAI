from django.urls import path
from .views import GenerateCodeView

urlpatterns = [
    path("generate/", GenerateCodeView.as_view(), name="generate_code"),
]