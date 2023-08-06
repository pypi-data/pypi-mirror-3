import logging
import os
import sys
import traceback

from webob import Request, exc

import pkg_resources
dv = pkg_resources.working_set.by_key.get('django').version
MIN_VERSION = '1.0.3'

from django.core.handlers.wsgi import WSGIHandler
from django import conf

class FakeSettings(conf.LazySettings):
    """
    Fake replacement for django.conf.settings
    Ensure to zap python modules's caching system
    """
    def __init__(self):
        setattr(self, 'fake_settings_modules', {})

    def load(self, module=None):
        if not module:
            module = os.environ[conf.ENVIRONMENT_VARIABLE]
        if not module in  self.fake_settings_modules:
            # try to load the module
            settings = conf. LazySettings()
            self.fake_settings_modules[module] = settings
        return module, self.fake_settings_modules[module]

    def __getattribute__(self, attr):
        if attr == '__file__':
            # This one I don't really mind
            raise AttributeError("Is it really happens? " + \
                "You want to retrieve __file__ but I'm a virtual module")
        not_wrapped = ['fake_settings_modules', 'load',
                       'configure', '_target', 'get_target',
                       'configure', 'configured']
        if not attr in not_wrapped:
            modulename, module = self.load()
            if modulename in self.fake_settings_modules:
                return getattr(module, attr)
            else:
                raise Exception('Cannot load %s' % module)
        else:
            return object.__getattribute__(self, attr)

    def __setattr__(self, name, value):
        not_wrapped = ['fake_settings_modules', 'load',
                       'configure', '_target', 'get_target',
                       'configure', 'configured']
        if not name in not_wrapped:
            modulename, module = self.load()
            if name == '_target':
                pass
            else:
                setattr(module, name, value)
        else:
            object.__setattr__(self, name, value)

    def __getattr__(self, name):
        return getattr(self._target, name)

    def _import_settings(self):
        """
        Load the settings module pointed to by the environment variable. This
        is used the first time we need any settings at all, if the user has not
        previously configured the settings manually.
        """
        self.load()

    def get_target(self):
        _, module = self.load()
        return module
    _target = property(get_target)

    def configure(self, default_settings=conf.global_settings, **options):
        """
        Called to manually configure the settings. The 'default_settings'
        parameter sets where to retrieve any unspecified values from (its
        argument must support attribute access (__getattr__)).
        """
        modulename, module = self.load()
        holder = UserSettingsHolder(default_settings)
        for name, value in options.items():
            setattr(holder, name, value)
        self.settings_modules[modulename] = self.settings_modules

    def configured(self):
        """
        Returns True if the settings have already been configured.
        """
        return bool(len(self.settings_modules.keys()))
    configured = property(configured)

def django_factory(global_config, **local_config):
    """
    A paste.httpfactory to wrap a django WSGI based application.
    """
    apps = {}
    log = logging.getLogger('dj.paste')
    wconf = global_config.copy()
    wconf.update(**local_config)
    debug = False
    if global_config.get('debug', 'False').lower() == 'true':
        debug = True
    if debug:
        if dv < MIN_VERSION:
            # This is only needed for Django versions < [7537]:
            def null_500_response(request, exc_type, exc_value, tb):
                raise exc_type, exc_value, tb
            from django.views import debug
            debug.technical_500_response = null_500_response
    dmk = 'django_settings_module'
    dsm = wconf.get(dmk, '').strip()
    if wconf.get('multi', '') == 'true':
        conf.settings = FakeSettings()
    app = WSGIHandler()
    def django_app(environ, start_response):
        os.environ[conf.ENVIRONMENT_VARIABLE] = dsm
        req = Request(environ)
        try:
            resp = req.get_response(app)
            return resp(environ, start_response)
        except Exception, e:
            if not debug:
                log.error('%r: %s', e, e)
                log.error('%r', environ)
                return exc.HTTPServerError(str(e))(environ, start_response)
            else:
                raise
    return django_app

def django_multi_factory(global_config, **local_config):
    """
    A paste.httpfactory to wrap a django WSGI based application.
    """
    if not local_config: local_config = {}
    local_config['multi'] = 'true'
    return django_factory(global_config, **local_config)

