from django.conf import settings
from sqlalchemy import create_engine, text
from sqlalchemy.exc import ProgrammingError

from .config import TABLE_NAME_TEMPLATE
from .models import Document


def get_transform_data(document_id):
    file = Document.objects.get(pk=document_id)
    db_settings = settings.DATABASES['default']
    db_url = (
        f"postgresql+psycopg://{db_settings['USER']}:{db_settings['PASSWORD']}"
        f"@{db_settings['HOST']}:{db_settings['PORT']}/{db_settings['NAME']}"
    )
    transform_table_name = TABLE_NAME_TEMPLATE.format(document_id=document_id) + '_RESULT'
    connection = create_engine(db_url).connect()
    query = 'SELECT * FROM ' + transform_table_name
    try:
        cursor = connection.execute(text(query))
        columns = cursor.keys()
        data = cursor.fetchall()
        connection.close()
        return columns, data
    except ProgrammingError as e:
        file.status = Document.Statuses.FAILED
        file.save()
        raise e
