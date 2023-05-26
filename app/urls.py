from django.urls import path, include
from . import views

urlpatterns = [
    path('upload', views.FileUploadView.as_view()),
    path('create-tag', views.CreateTag.as_view()),
    path('update-tag/<str:tag_id>', views.UpdateTag.as_view()),
    path('get-aspects/<str:sheet_id>', views.GetAvaliableAspects.as_view()),
    path('get-sentiments/<str:sheet_id>', views.GetAvaliableSentiments.as_view()),
    path('labeled-sheet-data/<str:sheet_id>', views.GetTextDataWithTags.as_view()),
]