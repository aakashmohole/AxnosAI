from django.shortcuts import render
import psycopg2
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from chat_config.models import Chat
from chat_config.serializers import ChatSerializer
from .utils.pool import get_connection_pool
import pandas as pd

import warnings
warnings.filterwarnings('ignore')

# API 1: Get Database URL by chat_id
class ConnectDatabaseAPIView(APIView):
     """
    API to connect to DB using chat_id and return status
    """
    
     def get(self, request, chat_id):
        print(chat_id)
        chat_db = get_object_or_404(Chat, id=chat_id)
        db_url = chat_db.dataset        #url and dataset saved in dataset col 

        try:
            pool = get_connection_pool(chat_id, db_url)
            print("Pool connected successfuly!")
            conn = pool.getconn()
            pool.putconn(conn)
            print("Opening connection")
            return Response({"message": "Database connection successful!"}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        

class ShowTablesAPIView(APIView):
    """
    API to fetch all tables in DB using chat_id
    """
    def get(self, request, chat_id):
        chat_db = get_object_or_404(Chat, id=chat_id)
        db_url = chat_db.dataset

        try:
            pool = get_connection_pool(chat_id, db_url)
            conn = pool.getconn()
            cursor = conn.cursor()
            cursor.execute("""SELECT table_name FROM information_schema.tables WHERE table_schema='public'""")
            tables = [row[0] for row in cursor.fetchall()]
            print(tables)
            cursor.close()
            pool.putconn(conn)
            return Response({"tables": tables}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        
        


class FetchTablesDataAPIView(APIView):
    """
    API to fetch all rows from tables and return as DataFrame JSON
    """
    def post(self, request, chat_id):
        chat_db = get_object_or_404(Chat, id=chat_id)
        db_url = chat_db.dataset
        table_names = request.data.get("tables", [])

        if not table_names or not isinstance(table_names, list):
            return Response({"error": "Provide a list of table names"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            pool = get_connection_pool(chat_id, db_url)
            conn = pool.getconn()
            all_data = {}

            for table in table_names:
                query = f'SELECT * FROM "{table}"'  # use quotes to avoid case issues
                df = pd.read_sql(query, conn)
                all_data[table] = df.to_dict(orient="records")  # convert DataFrame to list of dicts

            pool.putconn(conn)
            return Response({"data": all_data}, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)