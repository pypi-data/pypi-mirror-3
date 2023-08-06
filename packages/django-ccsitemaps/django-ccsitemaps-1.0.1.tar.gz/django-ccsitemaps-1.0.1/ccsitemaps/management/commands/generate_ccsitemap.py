from django.core.management.base import BaseCommand, CommandError
from django.conf import settings
from django.contrib.sites.models import Site
from django.template import loader, Context
import ccsitemaps


class Command(BaseCommand):
    help = 'Generates a static sitemap'


    def handle(self, *args, **options):
        # auto discover
        ccsitemaps.autodiscover()
        # write the index
        t = loader.get_template('ccsitemaps/index.xml')
        # build the context
        c = Context({
                'site': Site.objects.get_current(),
                'sitemaps': ccsitemaps.Registry.registry().values()
            })
        rendered = t.render(c)
        # write it out
        with open('%ssitemap.xml' % settings.STATIC_ROOT, 'w') as root:
            root.write(rendered)
        # write the individual sitemaps
        for sitemap in ccsitemaps.Registry.registry().values():
            # the filename
            fname = '%ssitemap-%s.xml' % (
                    settings.STATIC_ROOT, sitemap.key)
            # the template
            template = sitemap.template or 'ccsitemaps/node.xml'
            # load it
            t = loader.get_template(template)
            # build the context
            c = Context({
                    'site': Site.objects.get_current(),
                    'objects': sitemap.get_objects()
                })
            # render ir
            rendered = t.render(c)
            # write it out
            with open(fname, 'w') as node:
                node.write(rendered)

