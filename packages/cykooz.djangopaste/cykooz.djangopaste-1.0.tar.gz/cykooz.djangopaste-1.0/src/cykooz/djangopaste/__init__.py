def make_django(global_config, **kw):
    settings = kw.get('settings')
    if settings is None:
        raise ValueError('Must provide "settings" value')

    import os
    os.environ['DJANGO_SETTINGS_MODULE'] = settings
    from django.core.handlers.wsgi import WSGIHandler
    return WSGIHandler()
