# Copyright (C) 2011 Linaro Limited
#
# Author: Zygmunt Krynicki <zygmunt.krynicki@linaro.org>
#
# This file is part of django-debian.
#
# django-debian is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License version 3
# as published by the Free Software Foundation
#
# django-debian is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with django-debian.  If not, see <http://www.gnu.org/licenses/>.

"""
dbconfig-common integration for django
"""

import os

from django_debian.config_file import ConfigFile


def get_database(pathname):
    """
    Get django database settings for dbconfig-common file generated with
    dbconfig-generate-include in thg default shell mode.
    """
    config = ConfigFile.load(pathname)
    if config.dbtype == "sqlite3":
        ENGINE = "django.db.backends.sqlite3"
        NAME = os.path.join(config.basepath, config.dbname)
    elif config.dbtype == "mysql":
        ENGINE = "django.db.backends.mysql"
        NAME = config.dbname
    elif config.dbtype == "pgsql":
        ENGINE = "django.db.backends.postgresql_psycopg2"
        NAME = config.dbname
        # Work around for http://bugs.debian.org/cgi-bin/bugreport.cgi?bug=509627
        if config.dbserver == "":
            config.dbserver = "localhost"
    else:
        raise ValueError("Unupported value for dbtype: %r" % config.dbtype)
    return {
        'ENGINE': ENGINE,
        'NAME': NAME,
        'USER': config.dbuser,
        'PASSWORD': config.dbpass,
        'HOST': config.dbserver,
        'PORT': config.dbport}
