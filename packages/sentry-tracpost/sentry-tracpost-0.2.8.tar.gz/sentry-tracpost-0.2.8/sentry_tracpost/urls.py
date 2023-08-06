from django.conf.urls.defaults import *
from sentry_tracpost.plugin import start
uuid_re = r'\b[A-F0-9]{8}(?:-[A-F0-9]{4}){3}-[A-Z0-9]{12}\b|$'

urlpatterns = patterns('',
    url(r'^tracpost/(?P<group_id>\d+)/$', 'start', name='send_message'),
)
