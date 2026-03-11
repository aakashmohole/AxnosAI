from django.urls import path
from .views import ExecuteGeneratedCodeView, UpdateGeneratedCodeView

urlpatterns = [
    path("execute/<int:pk>/", ExecuteGeneratedCodeView.as_view(), name="execute"),
    path("update/<int:pk>/", UpdateGeneratedCodeView.as_view(), name="update"),
]

