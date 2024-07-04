from django.urls import path
from . import views

urlpatterns = [
    path('', views.upload_file, name='upload_file'),
    path('success/<int:file_id>', views.file_upload_success, name='file_upload_success'),
    path('check_status/<int:file_id>/', views.check_status, name='check_status'),
]
