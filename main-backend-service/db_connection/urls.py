from django.urls import path
from .views import ConnectDatabaseAPIView, ShowTablesAPIView, FetchTablesDataAPIView

urlpatterns = [
    path("connect/<str:chat_id>/", ConnectDatabaseAPIView.as_view(), name="connect-database"),
    path("fetch-tables/<str:chat_id>/", ShowTablesAPIView.as_view(), name="show-tables"),
    path("fetch-table-recoreds/<str:chat_id>/", FetchTablesDataAPIView.as_view(), name="show-table-records"),
]
