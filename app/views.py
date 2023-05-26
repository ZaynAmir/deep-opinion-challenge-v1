from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.pagination import PageNumberPagination
from django.db import transaction
import pandas as pd
import os
import openpyxl
import sqlite3
from .models import SheetModel, TrainingData, Tag
from .serializers import TagSerializer




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
            return Response({"success": True, "sheet_id":sheet.id, "message": f"{file_name} uploaded."} ,status=status.HTTP_201_CREATED)
        except Exception as e:
            print(e)
            return Response({'error': 'Internal Server Error'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        

class CreateTag(APIView):
    def post(self, request, *args, **kwargs):
            try:
                aspect = request.data.get("aspect")
                sentiment = request.data.get("sentiment")
                data_id = request.data.get("text_id")
                if not aspect or not sentiment or not data_id:
                    hint = {
                        "text_id": "required",
                        "sentiment": "required",
                        "aspect": "required"
                    }
                    return Response({"success": False, 'error': 'request payload is not complete', "hint": hint }, status=status.HTTP_400_BAD_REQUEST)
                if sentiment not in ["POS", "NEG", "NEU"]:
                    return Response({"success": False, 'error': 'sentiment is not in ("POS", "NEG", "NEU")'}, status=status.HTTP_400_BAD_REQUEST)
                with transaction.atomic(): # applying rollback transaction to make sure data integrity
                    new_tag = Tag.objects.create(aspect=aspect, sentiment=sentiment)
                    training_data =  TrainingData.objects.get(id=data_id)
                    training_data.tags.add(new_tag)
                    training_data.save()
                return Response({"success": True, "tag_id": new_tag.id,  "message": "tag is created" } ,status=status.HTTP_201_CREATED)
            except TrainingData.DoesNotExist:
                return Response({"success": False, 'error': 'text_id on which you are trying to create tag is not avaliable'}, status=status.HTTP_400_BAD_REQUEST)
            except:
                return Response({"success": False, 'error': 'Internal Server Error'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            
class UpdateTag(APIView):
    def put(self, request, *args, **kwargs):
            try:
                tag_id = kwargs["tag_id"]
                tag_instance =  Tag.objects.get(id=tag_id)
                serializer = TagSerializer(instance=tag_instance, data=request.data ,partial=True)
                if serializer.is_valid(raise_exception=True):
                    serializer.save()
                    return Response({"success": True,  "message": "tag is updated", "data":serializer.data } ,status=status.HTTP_200_OK)
            except Tag.DoesNotExist:
                return Response({"success": False, 'error': 'tag which you are trying to update is not avaliable'}, status=status.HTTP_400_BAD_REQUEST)
            

class GetAvaliableAspects(APIView):
    def get(self, request, *args, **kwargs):
        sheet_id = kwargs["sheet_id"]
        try:
            sheet = SheetModel.objects.get(id=sheet_id)
        except SheetModel.DoesNotExist:
            return Response({"success": False, 'error': f'sheet with id: {sheet_id} is not avaliable'}, status=status.HTTP_400_BAD_REQUEST)
        queryset = Tag.objects.filter(trainingdata__sheet=sheet).values("aspect").distinct().order_by("aspect")
        paginator = PageNumberPagination()
        paginator.page_size = request.query_params.get('page_size', 10)  # Number of items per page
        paginated_queryset = paginator.paginate_queryset(queryset, request)
        return paginator.get_paginated_response(paginated_queryset)
    
class GetAvaliableSentiments(APIView):
    def get(self, request, *args, **kwargs):
        sheet_id = kwargs["sheet_id"]
        try:
            sheet = SheetModel.objects.get(id=sheet_id)
        except SheetModel.DoesNotExist:
            return Response({"success": False, 'error': f'sheet with id: {sheet_id} is not avaliable'}, status=status.HTTP_400_BAD_REQUEST)
        # queryset = Tag.objects.all().values("sentiment").distinct()
        queryset = Tag.objects.filter(trainingdata__sheet=sheet).values("sentiment").distinct().order_by("sentiment")
        paginator = PageNumberPagination()
        paginator.page_size = request.query_params.get('page_size', 10)  # Number of items per page
        paginated_queryset = paginator.paginate_queryset(queryset, request)
        return paginator.get_paginated_response(paginated_queryset)
    

class GetTextDataWithTags(APIView):
    def get(self, request, *args, **kwargs):
        document_id = kwargs["sheet_id"]
        if SheetModel.objects.filter(id=document_id).exists():
            queryset = TrainingData.objects.filter(sheet=document_id)
            paginator = PageNumberPagination()
            paginator.page_size = request.query_params.get('page_size', 10)  # Number of items per page
            paginated_queryset = paginator.paginate_queryset(queryset, request)
            data = [{"id": item.id, "text": item.text, "tags": TagSerializer(instance=item.tags.all(), many=True).data} for item in paginated_queryset]
            return paginator.get_paginated_response(data)

        return Response({"success": False, "error": f"Sheet with id: {document_id} is not found"}, status=status.HTTP_404_NOT_FOUND)