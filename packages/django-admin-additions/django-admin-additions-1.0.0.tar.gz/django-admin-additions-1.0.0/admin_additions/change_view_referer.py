"""
This method of returning to the filtered view after submitting a form in an admin
change view is based largely upon http://djangosnippets.org/snippets/2531/

The changes:

    - Don't use a literal {} in a function/method declaration. It really is bad.
    - Use request.METHOD to determine if we want to set or use the referer.
    - Monkey patch all admin models.
    
"""

from django.contrib.admin import ModelAdmin
from django import forms

old_change_view = ModelAdmin.change_view

def change_view(self, request, object_id, extra_content=None):
    result = old_change_view(self, request, object_id, extra_content)
    
    if request.method != 'POST':
        ref = request.META.get('HTTP_REFERER', None)
        if ref:
            request.session['filtered'] = ref
    elif request.POST.has_key('_save'):
        if request.session.get('filtered', None):
            result['Location'] = request.session['filtered']
            request.session['filtered'] = None
    
    return result

ModelAdmin.change_view = change_view