
import httplib2
import wsgi_intercept
import shutil
import os
import sys

from tiddlywebplugins.instancer.util import spawn
import tiddlywebplugins.prettyerror.instance as instance_module
from tiddlywebplugins.prettyerror.config import config as init_config

from tiddlywebplugins.prettyerror import init


from wsgi_intercept import httplib2_intercept

from tiddlyweb.store import Store

def make_test_env():
    try:
        shutil.rmtree('test_instance')
    except OSError:
        pass
    spawn('test_instance', init_config, instance_module)


def setup_module(module):
    make_test_env()
    from tiddlyweb.web import serve
    from tiddlyweb.config import config
    init(config)
    def app_fn():
        return serve.load_app()
    httplib2_intercept.install()
    wsgi_intercept.add_wsgi_intercept('0.0.0.0', 8080, app_fn)
    module.store = Store(config['server_store'][0],
            config['server_store'][1], {'tiddlyweb.config': config})
    module.http = httplib2.Http()


def test_selector_404():
    response, content = http.request('http://0.0.0.0:8080/fake',
            method='GET')
    assert response['status'] == '404'
    assert response['content-type'] == 'text/html; charset=UTF-8'
    assert 'Path not found for "/fake"' in content


def test_tiddlyweb_404():
    response, content = http.request('http://0.0.0.0:8080/bags/fake',
            method='GET')
    assert response['status'] == '404'
    assert response['content-type'] == 'text/html; charset=UTF-8'
    assert 'Path not found for "/bags/fake"' in content
