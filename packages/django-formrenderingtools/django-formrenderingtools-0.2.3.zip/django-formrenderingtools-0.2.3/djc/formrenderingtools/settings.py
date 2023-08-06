"""Application settings."""

# Default settings
DEFAULT_SETTINGS = {
    'FORMRENDERINGTOOLS_TEMPLATE_DIR': 'form_layouts',
    'FORMRENDERINGTOOLS_DEFAULT_LAYOUT': 'default',
    'FORMRENDERINGTOOLS_FORM_TEMPLATE_DIR': 'form',
    'FORMRENDERINGTOOLS_FORM_ERRORS_TEMPLATE_DIR': 'form_errors',
    'FORMRENDERINGTOOLS_FIELD_LIST_TEMPLATE_DIR': 'field_list',
    'FORMRENDERINGTOOLS_FIELD_TEMPLATE_DIR': 'field',
    'FORMRENDERINGTOOLS_FIELD_ERRORS_TEMPLATE_DIR': 'field_errors',
    'FORMRENDERINGTOOLS_LABEL_TEMPLATE_DIR': 'label',
    'FORMRENDERINGTOOLS_HELP_TEXT_TEMPLATE_DIR': 'help_text',
    'FORMRENDERINGTOOLS_DEFAULT_TEMPLATE': 'default.html',
}

def update_django_settings():
    """Initializes djc.formrenderingtools settings in Django's configuration.
    
    User-defined settings are not overridden.
    """
    # Don't import settings globally, so that settings loading happens lately
    from django.conf import settings
    
    for key, value in DEFAULT_SETTINGS.iteritems():
        if not hasattr(settings, key):
            setattr(settings, key, value)
