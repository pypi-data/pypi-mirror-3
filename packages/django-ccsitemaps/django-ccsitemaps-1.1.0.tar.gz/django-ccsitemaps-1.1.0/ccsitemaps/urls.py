from django.conf.urls import patterns, include, url

urlpatterns = patterns('',
   url(r'^.xml',
       'ccsitemaps.views.index',
        name='root'),
   url(r'^(?P<key>[\w\-]+).xml',
       'ccsitemaps.views.index',
        name='node'),
)
