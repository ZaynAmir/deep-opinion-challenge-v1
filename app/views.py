from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
import pandas as pd
import os
import openpyxl
import sqlite3
from .models import SheetModel, TrainingData, Tag




class FileUploadView(APIView):
    def post(self, request, format=None):
        file = request.FILES['file']

        if file.name.endswith('.csv'):
            df = pd.read_csv(file)
        elif file.name.endswith('.xlsx'):
            df = pd.read_excel(file)
        else:
            return Response({'error': 'Invalid file format'}, status=status.HTTP_400_BAD_REQUEST)
        try:
            column = df.columns.to_list()[0]
            df_to_dict = df.to_dict('records')
            file_name = os.path.basename(file.name)
            rows_count = len(df_to_dict)

            sheet = SheetModel.objects.create(
                name = file_name,
                row_count = rows_count
            )
            conn = sqlite3.connect('db.sqlite3')

            # Increase the cache size
            conn.execute("PRAGMA cache_size = 6000000")  # 3GB cache size

            # Set journaling mode to memory
            conn.execute("PRAGMA journal_mode = MEMORY")

            # Disable indexing while inserting
            conn.execute("PRAGMA defer_foreign_keys = ON")
            conn.execute("PRAGMA synchronous = OFF")
            conn.execute("PRAGMA count_changes = OFF")
            conn.execute("PRAGMA temp_store = MEMORY")

            # Create a cursor object
            cursor = conn.cursor()

            sql = "INSERT INTO app_trainingdata (text, sheet_id) VALUES (?, ?)"
            # Prepare the data for insertion (a list of tuples)
            data = [(item[column], sheet.id) for item in df_to_dict if item[column] is not None and str(item[column]) != 'nan']

            # Execute the bulk insert
            cursor.executemany(sql, data)

            # Commit the changes
            conn.commit()

            # Close the cursor and the connection
            cursor.close()
            conn.close()
            return Response({"success": True, "document_id":sheet.id, "message": f"{file_name} uploaded."} ,status=status.HTTP_201_CREATED)
        except Exception as e:
            print(e)
            return Response({'error': 'error in database connectivity'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
