from django.conf.urls.defaults import patterns, include, url

urlpatterns = patterns('postit.views',
	url(r'^$', 'postit', name='postit'),
	url(r'^delete/(?P<id>\d+)/$', 'postit_delete', name='postit_delete'),
    url(r'^new/$', 'postit_edit_or_new', name='postit_edit_or_new'),
    url(r'^new/(?P<id>\d+)/$', 'postit_edit_or_new', name='postit_edit_or_new'),
    url(r'^filter/(?P<filter>[-\w]+)/(?P<selector>[-\w]+)/$', 'postit_by_filter', name='postit_by_filter'),
    url(r'^export/$', 'postit_export', name='postit_export'),
)