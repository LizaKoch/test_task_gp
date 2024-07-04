import dramatiq
import pandas as pd
from django.conf import settings
from sqlalchemy import create_engine, text
from sqlalchemy.exc import ProgrammingError

from .config import TABLE_NAME_TEMPLATE, TRANSFORM_QUERY_TEMPLATE, POSTFIX_TABLE_RESULT
from .models import Document


@dramatiq.actor(queue_name="default.DQ")
def remove_file(document_id):
    try:
        file = Document.objects.get(pk=document_id)
        file.document.delete(save=True)
        file.delete()
    except Document.DoesNotExist:
        pass

@dramatiq.actor(queue_name="default.DQ")
def update_file(document_id, format='csv'):
    file = Document.objects.get(pk=document_id)
    if format == 'csv':
        df = pd.read_csv(file.document, na_values=(' ', '-'))
    elif format in ('xlsx', 'xls'):
        df = pd.read_excel(file.document, na_values=(' ', '-'))
    else:
        raise ValueError('Invalid format')
    file.row_count = df.shape[0]
    file.save()

    db_settings = settings.DATABASES['default']
    db_url = (
        f"postgresql+psycopg://{db_settings['USER']}:{db_settings['PASSWORD']}"
        f"@{db_settings['HOST']}:{db_settings['PORT']}/{db_settings['NAME']}"
    )
    df = convert_column_types(df)
    connection = create_engine(db_url).connect()
    df.to_sql(
        TABLE_NAME_TEMPLATE.format(document_id=document_id),
        if_exists='replace',
        index=False,
        con=connection
    )
    connection.close()
    remove_file.send(document_id)
    return document_id


@dramatiq.actor(queue_name="default.DQ")
def transform_data(_metadata_prev_task, document_id):
    file = Document.objects.get(pk=document_id)
    db_settings = settings.DATABASES['default']
    db_url = (
        f"postgresql+psycopg://{db_settings['USER']}:{db_settings['PASSWORD']}"
        f"@{db_settings['HOST']}:{db_settings['PORT']}/{db_settings['NAME']}"
    )
    connection = create_engine(db_url).connect()
    source_table_name = TABLE_NAME_TEMPLATE.format(document_id=document_id)
    query = TRANSFORM_QUERY_TEMPLATE.format(
        table_name=source_table_name,
        transform_query=file.transform_query.format(table_name=source_table_name),
        result_postfix=POSTFIX_TABLE_RESULT,
    )
    try:
        connection.execute(text(query))
    except ProgrammingError as e:
        file.status = Document.Statuses.FAILED
        file.save()
        return
    connection.commit()
    connection.close()
    file.status = Document.Statuses.SUCCESS
    file.save()


@dramatiq.actor(queue_name="default.DQ")
def failure_document(exception, document_id):
    file = Document.objects.get(pk=document_id)
    file.status = Document.Status.FAILED
    file.save()
    print(f'Error: {exception}')


def convert_column_types(df):
    for col in df.columns:
        _number = pd.to_numeric(df[col], errors='coerce')

        if _number.notna().any() and _number.dropna().apply(lambda x: isinstance(x, (int, float))).all():
            df[col] = _number
            continue
        _dt = pd.to_datetime(df[col], errors='coerce')

        if _dt.notna().any() and _dt.dropna().apply(lambda x: isinstance(x, pd.Timestamp)).all():
            df[col] = _dt
            continue
    return df
