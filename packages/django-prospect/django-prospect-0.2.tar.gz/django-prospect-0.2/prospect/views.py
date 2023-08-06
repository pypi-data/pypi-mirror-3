from intranet.base_views import IntranetListView

class ProspectListView(IntranetListView):
    list_display = ('company_name', 'last_name', 'field')
    list_display_links = ('company_name',)
    search_fields = (
        'company_name',
        'first_name',
        'last_name',
        'field__name',
        'profession',
        'city',
    )

