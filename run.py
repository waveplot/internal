#!/usr/bin/env python2
# -*- coding: utf8 -*-

# Copyright (C) 2014  Ben Ockmore

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

"""Script to initialize the webservice app and run the debug server."""

from wpinternal import create_app
from wpinternal.config import DATABASE, GMAIL

config = {
    'SQLALCHEMY_DATABASE_URI':'postgresql://{}:{}@{}/{}'.format(
        DATABASE['username'],
        DATABASE['password'],
        DATABASE['host'],
        DATABASE['name']
    ),
    'MAIL_SERVER': 'smtp.gmail.com',
    'MAIL_PORT': 587,
    'MAIL_USE_TLS': True,
    'MAIL_USERNAME': GMAIL['username'],
    'MAIL_PASSWORD': GMAIL['password'],
}

app = create_app(config)

if __name__ == '__main__':
    app.run(debug=True, port=19048, host="0.0.0.0")
