from django.db.models import get_model
from django.contrib import admin

def patch_model_admin(model, patch_function):
    """
    Patch an installed ModelAdmin.
    
    patch_function must take one argument, the ModelAdmin, and
    may mutate the object in place, or return a new ModelAdmin.
    """
    if isinstance(model, basestring):
        model = get_model(*model.split('.'))
    ModelAdmin = type(admin.site._registry.get(model))
    ModelAdmin = patch_function(ModelAdmin) or ModelAdmin
    admin.site.unregister(model)
    admin.site.register(model, ModelAdmin)

def add_inlines(model, *inlines):
    """
    Add an arbitrary number of inlines to the admin for
    the provided model.
    """
    inlines = list(inlines)
    for i, inline in enumerate(inlines):
        if not issubclass(inline, admin.options.InlineModelAdmin):
            inlines[i] = type("%sInline" % inline.__name__, (admin.StackedInline,), {"model": inline})
    
    def inner(admin):
        admin.inlines = tuple(admin.inlines) + tuple(inlines)
    
    patch_model_admin(model, inner)

def add_actions(model, *actions):
    def inner(admin):
        for action in actions:
            admin.actions.append(action)
    
    patch_model_admin(model, inner)

def patch_admin(model):
    def inner(function):
        patch_model_admin(model, function)
    return inner