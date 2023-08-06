from django.conf import settings
from django.template.defaultfilters import slugify
from webutils.helpers import grab_from_import


def import_setting_name(setting_name, default_obj=None):
    ''' Used to import an item from a value in the current 
        Django projects settings.py
        
        Example in settings.py:
        
            FORM_TO_IMPORT = 'myproject.myapp.forms.CustomForm'
        
        Then to grab this, just call import_setting_name:
        
            form = import_setting_name('FORM_TO_IMPORT')
        
        Pass 'default_obj' 
    '''
    if hasattr(settings, setting_name):
        try:
            return grab_from_import(
                getattr(settings, setting_name),
                as_from=True,
            )
        except ImportError, err:
            if default_obj is None:
                raise ImportError(str(err))
    return default_obj


def slugify_uniquely(s, queryset=None, field='slug'):
    '''
    --> Taken from django-crm models.py

    Returns a slug based on 's' that is unique for all instances of the given
    field in the given queryset.
    
    If no string is given or the given string contains no slugify-able
    characters, default to the given field name + N where N is the number of
    default slugs already in the database.
    '''
    new_slug = new_slug_base = slugify(s)
    if queryset is not None:
        queryset = queryset.filter(**{'%s__startswith' % field: new_slug_base})
        similar_slugs = [value[0] for value in queryset.values_list(field)]
        i = 1
        while new_slug in similar_slugs:
            new_slug = "%s%d" % (new_slug_base, i)
            i += 1
    return new_slug
