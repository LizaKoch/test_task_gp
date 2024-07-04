from django import forms
from .models import Document

DEFAULT_TRANSFORM_QUERY = """
with cte as (
	select "Статус заявки", count(*)  as cnt
	from {table_name}
	where 1=1
	and "Дата создания заявки" between '2023-08-20 00:00:00.000' and '2023-08-22 00:00:00.000'
	group by "Статус заявки"
)
select it."Статус заявки" as "Название", count(it.*) as "За указанный период", coalesce(c.cnt::text, '-') as "За все время" from 
{table_name} it
left join cte c on c."Статус заявки" = it."Статус заявки"
group by it."Статус заявки", c.cnt
""".strip()


class DocumentForm(forms.ModelForm):
    transform_query = forms.CharField(
        widget=forms.Textarea(attrs={'placeholder': 'Enter SQL query to transform data'}),
        initial=DEFAULT_TRANSFORM_QUERY
    )

    class Meta:
        model = Document
        fields = ('description', 'document', 'transform_query')
