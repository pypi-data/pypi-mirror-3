from django.contrib import admin as default_admin
from authy_admin.sites import AuthyAdminSite

__version_info__ = ('0', '1', '0')
__version__ = '.'.join(__version_info__)

# replace django's default admin site with our version
default_admin.site = AuthyAdminSite()
