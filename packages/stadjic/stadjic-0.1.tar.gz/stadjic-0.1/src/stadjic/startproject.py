from __future__ import with_statement
from django.core.management import call_command
from stadjic.pythonsource import PythonSource
from string import Template
import os.path


def start_project(path):
    def django_path(filename):
        return os.path.join(path, filename)
    
    project_name = os.path.basename(os.path.abspath(path))
    
    if os.path.exists(path):
        raise Exception('Can\'t create directory %s, file already exists' % (path,))
    
    call_command('startproject', path)
    
    os.mkdir(django_path('media'))
    os.mkdir(django_path('media/css'))
    os.mkdir(django_path('media/js'))
    os.mkdir(django_path('media/images'))
    os.mkdir(django_path('templates'))
    
    with PythonSource.file_edits(django_path('views.py'), create_if_not_exists=True) as source:
        source.add_imports(
            'from django.shortcuts import render_to_response',
            'from django.template import RequestContext',
            'import os.path',
        )
        
        source.dedent_and_append_code("""
            def render_template(request):
                path = request.path.strip('/')
                return render_to_response(
                    [os.path.join(path, 'index.html'), '%s.html' % path],
                    context_instance=RequestContext(request),
                )
        """)
    
    with PythonSource.file_edits(django_path('urls.py')) as source:
        source.add_imports(
            'from django.conf import settings',
            'import re',
        )
        
        source.dedent_and_append_code(Template("""
            if settings.DEBUG and settings.MEDIA_URL.startswith('/'):
                urlpatterns += patterns('',
                    url(
                        r'^%s/(?P<path>.*)$' % re.escape(settings.MEDIA_URL.strip('/')),
                        'django.views.static.serve',
                        {'document_root': settings.MEDIA_ROOT},
                    ),
                )
            
            
            urlpatterns += patterns('',
                # Render templates without a view. Must be the last url.
                url(r'^(?:.*/)?$', '${project_name}.views.render_template'),
            )
        """).safe_substitute(
            project_name=project_name,
        ))
    
    with PythonSource.file_edits(django_path('settings.py')) as source:
        source.add_imports(
            'import os.path',
        )
        
        source.replace_once(
            r'^(?m)MEDIA_ROOT\s=.*$',
            r"MEDIA_ROOT = os.path.join(os.path.dirname(__file__), 'media')",
        )
        
        source.replace_once(
            r'^(?m)MEDIA_URL\s=.*$',
            r"MEDIA_URL = '/media/'",
        )
        
        source.replace_once(
            r'^(?m)(TEMPLATE_DIRS\s*=\s*\(\s*)',
            r"\1os.path.join(os.path.dirname(__file__), 'templates'),\n    ",
        )
