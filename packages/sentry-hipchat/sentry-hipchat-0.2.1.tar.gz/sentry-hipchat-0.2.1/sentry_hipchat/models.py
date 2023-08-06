"""
sentry_hipchat.models
~~~~~~~~~~~~~~~~~~~~~

:copyright: (c) 2011 by Linovia, see AUTHORS for more details.
:license: BSD, see LICENSE for more details.
"""

from django import forms

from sentry.models import ProjectOption
from sentry.plugins import Plugin, register

import urllib
import urllib2
import json
import logging


class HipchatOptionsForm(forms.Form):
    token = forms.CharField(help_text="Your hipchat API token.")
    room = forms.CharField(help_text="Room name or ID.")


@register
class HipchatMessage(Plugin):
    author = 'Xavier Ordoquy'
    author_url = 'https://github.com/linovia/sentry-hipchat'
    title = 'Hipchat'
    conf_title = 'Hipchat'
    conf_key = 'hipchat'
    project_conf_form = HipchatOptionsForm

    def is_configured(self, project):
        return all((self.get_option(k, project) for k in ('room', 'token')))

    def post_process(self, group, event, is_new, is_sample, **kwargs):
        token = self.get_option('token', event.project)
        room = self.get_option('room', event.project)
        if token and room:
            self.send_payload(token, room, '[%s] %s' % (event.server_name, event.message))

    def send_payload(self, token, room, message):
        url = "https://api.hipchat.com/v1/rooms/message"
        values = {
            'auth_token': token,
            'room_id': room,
            'from': 'Sentry',
            'message': message,
            'notify': False,
            'color': 'red',
        }
        data = urllib.urlencode(values)
        request = urllib2.Request(url, data)
        response = urllib2.urlopen(request)
        raw_response_data = response.read()
        response_data = json.loads(raw_response_data)
        if 'status' not in response_data:
            logger = logging.getLogger('sentry.plugins.hipchat')
            logger.error('Unexpected response')
        if response_data['status'] != 'sent':
            logger = logging.getLogger('sentry.plugins.hipchat')
            logger.error('Event was not sent to hipchat')
