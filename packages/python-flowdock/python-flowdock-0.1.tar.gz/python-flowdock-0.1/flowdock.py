"""
flowdock.py
An API Client for FlowDock
https://www.flowdock.com/help/api_documentation
"""

__version__ = '0.1'

import os
import re
# http://docs.python-requests.org/
import requests

API_ENDPOINT = 'https://api.flowdock.com/v1/messages/influx/%(api_key)s'
EMAIL_RE = re.compile(
    r"(^[-!#$%&'*+/=?^_`{}|~0-9A-Z]+(\.[-!#$%&'*+/=?^_`{}|~0-9A-Z]+)*"  # dot-atom
    r'|^"([\001-\010\013\014\016-\037!#-\[\]-\177]|\\[\001-011\013\014\016-\177])*"' # quoted-string
    r')@(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?$', re.IGNORECASE  # domain
) # Thanks, Django!
PROJECT_RE = re.compile(r'^[a-z0-9_ ]+$', re.IGNORECASE)

DEFAULT_API_KEY=u''
DEFAULT_APP_NAME = u'Python FlowDock Client'
DEFAULT_PROJECT = None

if 'DJANGO_SETTINGS_MODULE' in os.environ:
    try:
        from django.conf import settings
    except ImportError:
        pass
    else:
        DEFAULT_API_KEY = getattr(settings, 'FLOWDOCK_API_KEY', DEFAULT_API_KEY)
        DEFAULT_APP_NAME = getattr(settings, 'FLOWDOCK_APP_NAME', DEFAULT_APP_NAME)
        DEFAULT_PROJECT = getattr(settings, 'FLOWDOCK_PROJECT', DEFAULT_PROJECT)

class FlowDocException(Exception): pass

class FlowDock(object):
    def __init__(self, api_key=None, app_name=None,
                 project=None):
        """FlowDock(api_key, app_name, project)

        api_key - Your FlowDock API key
        app_name - The source application name to list your post as "via"
        project - A more detailed categorization for your posts
        """
        self.api_key = api_key or DEFAULT_API_KEY
        assert self.api_key, u'An API key must be provided'
        self.app_name = app_name or DEFAULT_APP_NAME
        assert self.app_name, u'An app name must be given'
        self.project = project or DEFAULT_PROJECT

    @property
    def api_endpoint(self):
        return API_ENDPOINT % self.__dict__

    def post(self, from_address, subject, content,
             from_name=None, format='html', tags=[], link=None):
        """
        Post a message to FlowDock.

        Required args:
            from_address - Email address of the sender of this post
            subject - Subject of this post
            content - Content of this post

        Optional args:
            from_name - a human-readable name to go along with the from_address
            format - format of the content (default: 'html')
            tags - a list of strings to tag this post with
            link - a URL to associate with this post

        Returns True on success
        """
        assert EMAIL_RE.match(from_address), \
            u'The "from_address" must be a valid email address'
        assert subject, u'You must provide a subject'
        assert content, u'You must provide some content for this post'
        tags = map(unicode, tags)
        post_args = {
            'source': self.app_name,
            'from_address': from_address,
            'subject': subject,
            'content': content,
            'format': format
        }
        if from_name: post_args['from_name'] = from_name
        if tags: post_args['tags'] = ','.join(tags)
        if link: post_args['link'] = link
        if self.project: post_args['project'] = self.project
        response = requests.post(self.api_endpoint, data=post_args)
        if response.status_code == 500:
            raise FlowDocException(response.content)
        elif response.status_code == 200:
            return True
        response.raise_for_status()
        return False

def post(*args, **kwargs):
    client = FlowDock()
    return client.post(*args, **kwargs)
