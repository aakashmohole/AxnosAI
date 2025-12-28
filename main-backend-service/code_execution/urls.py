from django.urls import path
from .views import ExecuteGeneratedCodeView

urlpatterns = [
    path("execute/<int:pk>/", ExecuteGeneratedCodeView.as_view(), name="execute"),
]

