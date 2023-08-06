"""
A Django template loader that loads templates from a remote web site
"""
import datetime
import requests

from django.template import TemplateDoesNotExist
from django.template.loader import BaseLoader
from django.core import cache
from django.conf import settings

def _make_cache_key(url, permanent=False):
    """
    Make a unique cache key from a url
    """
    return "WebTemplate:%s:%s" % (url, {True:"p", False:"t"}[permanent])

def _get_setting(name, default):
    """
    Get a setting from `django.conf.settings`, with a default fallback
    """
    try:
        return getattr(settings, name)
    except AttributeError:
        return default


try:
    WEBCACHE = cache.get_cache('webtemplates')
except cache.InvalidCacheBackendError:
    WEBCACHE = cache.cache

try:
    WEBTEMPLATES = settings.WEBTEMPLATES
except AttributeError:
    raise AttributeError("WEBTEMPLATES must be defined in your settings.py")

PERMANENT_CACHE = _get_setting('WEBTEMPLATES_PERMANENT_CACHE', False)

# Cache for a year. If the external source is down for longer than that, you
# have bigger problems than your templates not being fresh!
PERMANENT_CACHE_TIME = datetime.timedelta(days=365).total_seconds()

TIMEOUT = _get_setting('WEBTEMPLATES_TIMEOUT', 3)

class Loader(BaseLoader):
    """
    Load templates for Django from a remote web site
    """
    is_usable = True

    def __init__(self, webcache=WEBCACHE, templates=WEBTEMPLATES,
        permanent=PERMANENT_CACHE, timeout=TIMEOUT):
        super(Loader, self).__init__()

        if not isinstance(templates, (list, tuple)):
            raise ValueError("templates should be a list or tuple, not %s"
                % type(templates))

        # `webcache` can be a cache name or an actual cache backend
        if isinstance(webcache, basestring):
            self.cache = cache.get_cache(webcache)
        else:
            self.cache = webcache

        self.permanent = permanent
        self.timeout = timeout

        self.templates = {}
        for template in templates:
            if isinstance(template, (tuple, list)):
                (remote, local) = template
            else:
                raise ValueError("Expected tuple for template name, not %s"
                    % type(template))
            
            self.templates[local] = remote

    def get_template_sources(self, name):
        """
        Return the paths searched for a template
        """
        if name in self.templates:
            return [self.templates[name]]
        return []

    def load_template_source(self, template_name, template_dirs=None):
        # We can only load templates that have been defined
        if template_name not in self.templates:
            raise TemplateDoesNotExist(template_name)

        url = self.templates[template_name]

        cache_key = _make_cache_key(url)
        permanent_cache_key = _make_cache_key(url, True)

        # Try and load from the cache
        cached = self.cache.get(cache_key)
        if cached is not None:
            return (cached, url)

        # Go and get it from the internets
        try:
            result = requests.get(url, timeout=self.timeout)
            success = result.status_code == 200
        except requests.exceptions.RequestException:
            success = False

        # Handle failures
        if not success:
            
            # Try and load something from the permanent cache
            if self.permanent:
                cached = self.cache.get(permanent_cache_key)
                if cached is not None:
                    return (cached, url)

            # Bail
            raise TemplateDoesNotExist(template_name)

        # Yay, a successful result! cache it and keep going
        template = result.text
        self.cache.set(cache_key, template)
        if self.permanent:
            self.cache.set(permanent_cache_key, template, PERMANENT_CACHE_TIME)

        return (template, url)
