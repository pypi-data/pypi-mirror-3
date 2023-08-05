from django.conf.urls.defaults import patterns, url

urlpatterns = patterns('pagehelp.views',
    url(r'^hide/$', 'set_default', {'show': False}, name='default_hide'),
    url(r'^show/$', 'set_default', {'show': True}, name='default_show'),
    url(r'^page/show/$', 'set_page', {'show': True}, name='page_show'),
    url(r'^page/hide/$', 'set_page', {'show': False}, name='page_hide'),
)
