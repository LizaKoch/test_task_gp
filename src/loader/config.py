POSTFIX_TABLE_RESULT = '_RESULT'
TABLE_NAME_TEMPLATE = 'loader_user_table_{document_id}'
TRANSFORM_QUERY_TEMPLATE = """
CREATE TABLE IF NOT EXISTS {table_name}{result_postfix} AS
{transform_query}
""".strip()
