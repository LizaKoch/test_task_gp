from django.shortcuts import render, redirect
from django.http import JsonResponse
from .forms import DocumentForm
from .models import Document
from .tasks import update_file
from .tasks import transform_data
from .tasks import failure_document
from .utils import get_transform_data


def upload_file(request):
    if request.method == 'POST':
        form = DocumentForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            file_id = form.instance.id
            file_format = form.files['document'].name.split('.')[-1]
            update_file.send_with_options(
                args=(file_id,),
                kwargs={'format': file_format},
                on_failure=failure_document,
                on_success=transform_data,
            )
            return redirect('file_upload_success', file_id=file_id)
    else:
        form = DocumentForm()
    return render(request, 'upload.html', {
        'form': form
    })


def file_upload_success(request, file_id):
    doc = Document.objects.filter(id=file_id).first()
    if not doc:
        return render(request, 'not_found.html')
    if doc.status == Document.Statuses.SUCCESS:
        # Файл успешно обработан, показываем таблицу с результатами
        columns, data = get_transform_data(doc.id)
        return render(request, 'transform_success.html', {'columns': columns, 'data': data})
    # Ожидание завершения обработки файла
    return render(request, 'upload_success.html', {'file_id': file_id})


def check_status(request, file_id):
    doc = Document.objects.filter(id=file_id).first()
    if not doc:
        return JsonResponse({'status': 'NOT_FOUND'})
    return JsonResponse({'status': doc.status})
