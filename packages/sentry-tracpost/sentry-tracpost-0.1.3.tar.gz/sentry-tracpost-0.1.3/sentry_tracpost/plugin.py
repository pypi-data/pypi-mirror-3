from django import forms

import socket
import sys
import xmlrpclib
import os
from array import array

from sentry.conf import settings
from sentry.plugins import Plugin

import pprint

import sentry_tracpost

class TracPostOptionsForm(forms.Form):
    xmlrpc_url = forms.URLField(required=True,
                          label='Trac XMLRPC URL',
                          help_text='e.g. https://user:pass@hostname.com:91/trac/login/rpc')

class TracPost(Plugin):
    title = 'TracPost'
    author = 'Josh Harwood'
    conf_title = 'TracPost'
    conf_key = 'tracpost'
    project_conf_form = TracPostOptionsForm

    def is_configured(self, project):
        return all((self.get_option(k, project) for k in ('xmlrpc_url')))

    def post_process(self, group, event, is_new, **kwargs):
        if not is_new or not self.is_configured(event.project):
            return
        rpc_srv = xmlrpclib.ServerProxy(self.get_option('xmlrpc_url', project),allow_none=True)
        socket.setdefaulttimeout(30)
	attrs = {'priority':"minor"}
	if event.message != None:
		pp = pprint.PrettyPrinter(indent=4)
	       	ticket_id = rpc_srv.ticket.create(event.message, "{{{\n" + str(pp.pformat(event.data)) + "\n}}}\n\nSee Sentry Page @ http://sentry.joinerysoft-directory.co.uk/jms/group/" + str(event.group_id), {'priority':"minor",}, False)
		print "New Ticket - " + str(ticket_id)
        return


