import os
from wrmota.views import _site, _admin
from wrmota.api import _api

class DefaultConfig(object):
    # default config inherited by all

    PROJECT = 'wrmota'
    VERSION = '2.0.0'

    DEBUG = False
    ASSETS_DEBUG = False

    LIBSASS_INCLUDES = ['_site/sass']
    EXTENSIONS = [
        {
            'name': 'js_lib',
            'bundle': [
                '_site/js/util.js',
                '_site/js/forms.js',
                '_site/js/touchclick.js',
                '_site/js/leaflet.js',
                '_site/js/howler-2.0.7.core.min.js',
            ],
            'filters': 'jsmin',
            'output': '_site/js/lib.min.js'
        },
        {
            'name': 'js_vue',
            'bundle': [
                '_site/js/vue-2.5.16.min.js',
                '_site/js/vue/svg.js',
            ],
            'filters': 'jsmin',
            'output': '_site/js/vue_lib.min.js'
        },
        {
            'name': 'css_site',
            'bundle': [
                '_site/css/leaflet.css',
                '_site/sass/main.sass',
            ],
            'filters': 'libsass,cssmin',
            'output': '_site/css/all.min.css',
            'depends': ['_site/sass/*', '_site/sass/**/*']
        },
        {
            'name': 'css_admin',
            'bundle': [
                '_admin/sass/main.sass',
            ],
            'filters': 'libsass,cssmin',
            'output': '_admin/css/admin.min.css',
            'depends': '_admin/sass/_*'
        },
    ]
    BLUEPRINTS = [_site, _api, _admin]

    ALLOWED_FILES = {
        'audio': set(['aiff', 'mp3', 'aac', 'm4a']),
        'image': set(['png', 'jpg', 'jpeg'])
    }

class DevConfig(DefaultConfig):
    ENVIRONMENT = 'DEVELOPMENT'
    DEBUG = True
    TESTING = False
    TEMPLATES_AUTO_RELOAD = True
    ASSETS_DEBUG = True

class ProdConfig(DefaultConfig):
    ENVIRONMENT = 'PRODUCTION'
    # config for production environment
    SERVER_NAME = 'wrmota.org'
    SERVER_PROTOCOL = 'https://'
    SEND_FILE_MAX_AGE_DEFAULT = 60*60*24*7*4

def get_config(MODE):
    SWITCH = {
        'DEVELOPMENT': DevConfig,
        'PRODUCTION': ProdConfig
    }
    return SWITCH[MODE]
