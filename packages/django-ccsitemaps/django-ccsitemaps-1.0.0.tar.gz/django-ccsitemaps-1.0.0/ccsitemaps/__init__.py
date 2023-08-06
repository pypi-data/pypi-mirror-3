version = (1, 0, 0)


def get_version():
    """returns a pep complient version number"""
    return '.'.join(str(i) for i in version)


def autodiscover():
    """
    auto discover brazenly copied from django.contrib.admin.
    """
    import copy
    from django.conf import settings
    from django.utils.importlib import import_module
    from django.utils.module_loading import module_has_submodule

    for app in settings.INSTALLED_APPS:
        try:
            mod = import_module(app)
        except importerror:
            pass
        try:
            before_import_registry = copy.copy(Registry._registry)
            b = import_module('%s.ccsitemap' % app)
        except Exception, e:
            Registry._registry = before_import_registry


def register(sitemap):
    """registers a sitemap with the registry"""
    Registry.add(sitemap)


class SiteMap(object):
    """the inheritable sitemap class"""

    model = None
    key = None
    template = None

    def last_mod(self):
        """returns the last modified date of the objects"""

    def get_objects(self):
        """returns the objects that will be included in the sitemap"""
        return None


class Registry(object):
    """the registry"""
    _registry = {}

    @staticmethod
    def registry():
        return Registry._registry

    @staticmethod
    def add(sitemap):
        key = Registry.key(sitemap)
        sitemap.key = key
        Registry._registry[key] = sitemap

    @staticmethod
    def key(sitemap):
        """returns a key for an instance or model class
        to query registry"""
        return '%s_%s' % (
                sitemap.model._meta.app_label,
                sitemap.model._meta.module_name)

    @staticmethod
    def get(sitemap):
        """returns the config"""
        key = Registry.key(sitemap)
        try:
            registry_item = Registry._registry[key]
        except KeyError:
            registry_item = None
        return registry_item
