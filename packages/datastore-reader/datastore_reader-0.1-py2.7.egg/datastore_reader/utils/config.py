# python import
import os, sys

# config obj
from ConfigObject import config_module


def _init_config_obj():
    # init path var
    config_path = '__no_config___'
    # config path passed
    if len(sys.argv) > 1\
    and os.path.exists(sys.argv[1]):
        config_path = sys.argv[1]
    # or in the current dir
    if not os.path.exists(config_path):
        config_path = 'config.ini'
    # or in the package by default
    if not os.path.exists(config_path):
        config_path = os.path.join(os.path.dirname(__file__),
                                   '..', '..', 'config.ini')
    # really no config!!
    if not os.path.exists(config_path):
        raise Exception('no config found!')
    # init config obj
    config_module(__name__, __file__, config_path)


# singleton flag
__initialized__ = False


# do init
if __initialized__ is False:
    # init config
    _init_config_obj()
    # update flag
    __initialized__ = True
