from django.conf.urls.defaults import patterns, url #, include

import settings

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'botnee_online.views.home', name='home'),
    # url(r'^botnee_online/', include('botnee_online.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    # url(r'^admin/', include(admin.site.urls)),

    #url(r'^(?P<input>[^/]+)$',  'web.interface.views.home'),
    url(r'home/',               'web.interface.views.home'),
    url(r'query/',              'web.interface.views.query'),
    url(r'dump/',               'web.interface.views.dump'),
    url(r'force_reindex/',      'web.interface.views.force_reindex'),
    url(r'delete/',             'web.interface.views.delete'),
    url(r'flush/',              'web.interface.views.flush'),
    url(r'matrix/',             'web.interface.views.get_matrix_summary'),
    url(r'meta/',               'web.interface.views.meta'),
    url(r'recalculate_idf/',    'web.interface.views.recalculate_idf'),
    url(r'dump_dictionaries/',  'web.interface.views.dump_dictionaries'),
    #url(r'^favicon\.ico$',      'django.views.generic.simple.redirect_to', {'url': '/images/favicon.ico'}),
    #url(r'^favicon\.ico$',      'django.views.generic.simple.redirect_to', {'url': '/web/images/favicon.ico'}),
    url(r'^static/(?P<path>.*)$', 'django.views.static.serve',
        {'document_root': settings.STATIC_ROOT, 'show_indexes': True}),
)

handler500 = 'web.interface.views.handler500'
