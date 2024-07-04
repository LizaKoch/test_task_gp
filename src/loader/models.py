from django.db import models
from loader.validators import validate_file_extension


class Status(models.TextChoices):
    PENDING = 'PENDING'
    SUCCESS = 'SUCCESS'
    FAILED = 'FAILED'


class Document(models.Model):

    Statuses = Status

    description = models.CharField(max_length=255, blank=True)
    document = models.FileField(upload_to='documents/', validators=[validate_file_extension])
    status = models.CharField(choices=Status.choices, default=Status.PENDING, max_length=20)
    transform_query = models.TextField(blank=True, default='')
    row_count = models.IntegerField(default=None, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.description
