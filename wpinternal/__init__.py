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

from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.mail import Mail

db = SQLAlchemy()
mail = Mail()


def add_cors_header(response):
    # https://github.com/jfinkels/flask-restless/issues/223
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Methods'] = \
        'HEAD, GET, POST, PATCH, PUT, OPTIONS, DELETE'
    response.headers['Access-Control-Allow-Headers'] = \
        'Origin, X-Requested-With, Content-Type, Accept'
    response.headers['Access-Control-Allow-Credentials'] = 'true'

    return response


def create_app(config):
    app = Flask(__name__)
    app.config.update(config)
    app.after_request(add_cors_header)

    db.app = app
    db.init_app(app)

    mail.init_app(app)

    from .index import index_views
    app.register_blueprint(index_views, url_prefix='/internal')

    from .registration import registration_views
    app.register_blueprint(registration_views, url_prefix='/internal')

    return app

