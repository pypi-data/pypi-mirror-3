from django.conf import settings
from django.contrib import admin

if hasattr(settings, 'ADMIN_ADDITIONS'):
    additions = settings.ADMIN_ADDITIONS
    
    if additions.get('RETURN_TO_FILTERED_CHANGELIST', False):
        import change_view_referer
    
    admin.ModelAdmin.save_on_top = additions.get('SAVE_ON_TOP', True)
    
    admin.options.list_select_related = additions.get('LIST_SELECT_RELATED', False)
    
    if additions.get('FULLY_DYNAMIC_FORMSETS', True):
        admin.options.InlineModelAdmin.extra = 0
    
    if additions.get('USE_LARGE_TABLE_PAGINATOR', False):
        from paginators import LargeTablePaginator
        admin.paginator = LargeTablePaginator