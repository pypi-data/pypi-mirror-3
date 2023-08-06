from celery import Celery

from celery.app import App
from celery.app import defaults
from celery.app.task import BaseTask
from celery.loaders import default as _default
from celery.utils import get_full_cls_name

def clean_quoted_config(config, key):
    # ini doesn't allow quoting, but lets support it to fit with celery
    config[key] = config[key].replace('"', '')

def includeme(config):
    convert_celery_options(config.registry.settings)
    celery.env = config.registry.settings
    conf = celery.loader.read_configuration()
    celery.config_from_object(conf)
    celery.config = config

TYPES_TO_OBJ = {
    'any': (object, None),
    'bool': (bool, defaults.str_to_bool),
    'dict': (dict, eval),
    'float': (float, float),
    'int': (int, int),
    'list': (list, eval),
    'tuple': (tuple, eval),
    'string': (str, None),
}

OPTIONS = {
    key: TYPES_TO_OBJ[opt.type]
    for key, opt in defaults.flatten(defaults.NAMESPACES)
#    if opt.type != 'string'
}

def convert_celery_options(config):
    """
    Converts celery options to apropriate types
    """

    for key, value in config.iteritems():
        opt_type = OPTIONS.get(key)

        if opt_type:
            if opt_type[0] is str:
                clean_quoted_config(config, key)
            elif opt_type[0] is object:
                try:
                    config[key] = eval(value)
                except:
                    pass  # any can be anything; even a string
            elif not isinstance(value, opt_type[0]):
                config[key] = opt_type[1](value)

class PyramidLoader(_default.Loader):
    def read_configuration(self):
        if self.app.env:
            config = self.app.env
            convert_celery_options(config)
            settings = self.setup_settings(config)
            self.configured = True
            return settings

        return {}


class PyramidCelery(App):
    loader_cls = get_full_cls_name(PyramidLoader)

    def __init__(self, env=None, *args, **kwargs):
        self.env = env
        super(PyramidCelery, self).__init__(*args, **kwargs)

    def __reduce_args__(self):
        return (self.env, ) + super(Celery, self).__reduce_args__()

celery = PyramidCelery()

class Task(BaseTask):
    app = celery
