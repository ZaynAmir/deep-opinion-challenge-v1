from django.urls import path, include
from . import views

urlpatterns = [
    path('upload', views.FileUploadView.as_view()),
    path('create-tag', views.CreateTag.as_view()),
]