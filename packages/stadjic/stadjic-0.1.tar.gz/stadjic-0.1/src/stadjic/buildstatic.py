from django.conf import settings
from django.test.client import Client
import os
import os.path
import re
import shutil


def build_static(dst_path):
    try:
        shutil.rmtree(dst_path)
    except (IOError, OSError,):
        if os.path.isdir(dst_path):
            raise
    
    copy_media(dst_path)
    print 'Copied media'
    
    ignore_patterns = tuple(
        re.compile(pattern)
        for pattern
        in getattr(settings, 'STADJIC_IGNORE', ())
    )
    for url, save_filename in iter_save_urls(dst_path, site_urls(), ignore_patterns):
        print 'Saved %s' % (url,)


def ensure_path(path):
    try:
        os.makedirs(path)
    except (IOError, OSError,):
        if not os.path.isdir(path):
            raise


def match_any(patterns, string):
    for pattern in patterns:
        if pattern.search(string):
            return True
    return False


def copy_media(dst_path):
    if not settings.MEDIA_URL.startswith('/'):
        raise Exception('Media must be hosted on the same domain')
    
    media_dst_path = os.path.join(dst_path, settings.MEDIA_URL.strip('/'))
    
    # Create the parent directory of media_dst_path
    ensure_path(os.path.dirname(media_dst_path))
    
    # Copy media files
    shutil.copytree(settings.MEDIA_ROOT, media_dst_path)


def iter_save_urls(dst_path, urls, ignore_patterns=()):
    client = Client()
    for url in urls:
        if match_any(ignore_patterns, url):
            continue
        
        if not url.startswith('/') or not url.endswith('/'):
            raise Exception('Can\'t save file for URL "%s"' % (url,))
        
        relative_path = url.strip('/')
        relative_filename = os.path.join(relative_path, 'index.html')
        
        save_path = os.path.join(dst_path, relative_path)
        save_filename = os.path.join(dst_path, relative_filename)
        
        html = client.get(url).content
        
        try:
            os.makedirs(save_path)
        except (IOError, OSError,):
            if not os.path.isdir(save_path):
                raise
        
        open(save_filename, 'wb').write(html.encode('utf8'))
        
        yield (url, save_filename,)


def site_urls():
    for template_dir in settings.TEMPLATE_DIRS:
        template_dir = os.path.abspath(template_dir)
        
        for path, dirnames, filenames in os.walk(template_dir):
            assert path[:len(template_dir)] == template_dir
            
            path_url = '/' + path[len(template_dir)+1:].replace(os.path.sep, '/')
            if not path_url.endswith('/'):
                path_url += '/'
            
            for filename in filenames:
                if not filename.endswith('.html'):
                    continue
                
                if filename == 'index.html':
                    yield path_url
                else:
                    yield '%s%s/' % (path_url, filename[:-5],)
