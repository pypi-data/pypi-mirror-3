from django.conf.urls.defaults import *
import plugin
uuid_re = r'\b[A-F0-9]{8}(?:-[A-F0-9]{4}){3}-[A-Z0-9]{12}\b|$'

urlpatterns = patterns('',
    url(r'^tracpost/$', 'plugin.TracPost.send_message', name='send_message'),
)
