from flask import Blueprint

_site = Blueprint(
    '_site',
    __name__,
    template_folder='../templates/site',
    static_folder='../static/site',
    static_url_path='',
    url_prefix=''
)
_admin = Blueprint(
    '_admin',
    __name__,
    template_folder='../templates',
    static_folder='../static/admin',
    static_url_path='/static/admin',
    subdomain='admin',
    url_prefix='',
)

from wrmota.views import site, admin
