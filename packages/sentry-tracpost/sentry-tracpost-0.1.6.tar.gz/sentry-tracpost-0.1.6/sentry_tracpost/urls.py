from django.conf.urls.defaults import *

urlpatterns = patterns('tracpost',
    url(r'^ticket/post/(?P<group_id>\d+)$', 'plugin.send_ticket', name='send_ticket'),
)
