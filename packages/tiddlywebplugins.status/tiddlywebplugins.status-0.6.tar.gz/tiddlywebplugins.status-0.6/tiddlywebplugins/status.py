"""
status is a TiddlyWeb plugins which gives a JSON report on
the current state of the server including:

* current user
* TiddlyWeb version
* available challengers

To use, add 'tiddlywebplugins.status' to 'system_plugins'
in 'tiddlywebconfig.py':

    config = {
        'system_plugins': [
            'tiddlywebplugins.status',
        ]
    }

Once running the plugin will add a route at
'{server_prefix}/status' that reports a JSON data
structure with the information described above.

If the request is made to /status.js, then the output
is the JSON encapsulated as JavaScript, so the info
can be loaded via a <script> tag in HTML. The data
ends up in the variable 'tiddlyweb.status'.

This is primarily used to determine who is the current
TiddlyWeb user. In TiddlySpace it provides additional
information.
"""

__author__ = 'Chris Dent (cdent@peermore.com)'
__copyright__ = 'Copyright UnaMesa Association 2008-2009'
__contributors__ = ['Frederik Dohr']
__license__ = 'BSD'


import simplejson
import tiddlyweb


def status(environ, start_response):
    data = _gather_data(environ)
    output = simplejson.dumps(data)
    start_response('200 OK', [
        ('Cache-Control', 'no-cache'),
        ('Content-Type', 'application/json')
        ])
    return [output]

def status_js(environ, start_response):
    data = _gather_data(environ)
    output = ('var tiddlyweb = tiddlyweb || {};\ntiddlyweb.status = %s;' %
            simplejson.dumps(data))
    start_response('200 OK', [
        ('Cache-Control', 'no-cache'),
        ('Content-Type', 'text/javascript')
        ])
    return [output]


def init(config):
    try:
        config['selector'].add('/status', GET=status)
        config['selector'].add('/status.js', GET=status_js)
    except KeyError:
        pass # not loaded as system_plugin


def _gather_data(environ):
    return {
            'username': environ['tiddlyweb.usersign']['name'],
            'version': tiddlyweb.__version__,
            'challengers': environ['tiddlyweb.config']['auth_systems'],
            }
