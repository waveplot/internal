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

import random
import string

import sqlalchemy.orm.exc
from flask import request, jsonify, Blueprint
from flask.ext.mail import Message
from wpschema import Editor

from wpinternal import db, mail
from wpinternal.config import SERVER, GMAIL

registration_views = Blueprint('registration_views', __name__)

def _is_valid_email(email):
    atpos = email.rfind('@')
    dotpos = email.rfind('.')

    if (atpos < 1) or (dotpos < (atpos + 2)) or ((dotpos + 2) >= len(email)):
        return False
    else:
        return True

def _generate_key():
    new_key = u"".join(
        random.choice(string.ascii_lowercase + string.digits) for _ in range(6)
    ).encode('ascii')

    while db.session.query(Editor).filter_by(key=new_key).first() is not None:
        new_key = u"".join(
            random.choice(string.ascii_lowercase + string.digits)
            for _ in range(6)
        ).encode('ascii')

    return new_key

@registration_views.route('/register', methods = ['POST'])
def register():
    data = request.json
    username = data['username']
    email = data['email']

    if not _is_valid_email(email):
        return jsonify({
            'success': False,
            'message': 'Invalid email address.',
        })

    existing = db.session.query(Editor).filter_by(email=email).first()
    if existing is not None:
        return jsonify({
            'success': False,
            'message': 'Email address already registered.',
        })

    new_editor = Editor(
        name=username,
        email=email,
        key=_generate_key()
    )

    db.session.add(new_editor)
    db.session.commit()

    activation_link = SERVER + '/activate/{}'.format(new_editor.key)
    msg = Message("Welcome to WavePlot!", recipients=[email],
                  sender=GMAIL['sender'])
    msg.html = (
        '<p>Hi {}!</p>'
        '<p>Please activate your WavePlot account using the activation link below:</p>'
        '<p><a href="{}">{}</a></p>'
        '<p>The above code is your editor key - besides using it to register, '
        'you\'ll also need it to upload any data to the website, so please '
        'keep this email!</p>'
        '<p>Many thanks for your help in building the WavePlot database!</p>'
    ).format(username, activation_link, new_editor.key)

    mail.send(msg)

    return jsonify({
        'success': True,
        'message': 'Registration successful.'
    })


@registration_views.route('/activate', methods = ['POST'])
def activate():
    data = request.json
    key = data['key']

    try:
        editor = db.session.query(Editor).filter_by(key=key).one()
    except sqlalchemy.orm.exc.NoResultFound:
        return jsonify({
            'success': False,
            'message': "Editor key invalid.",
        })

    if editor.active:
        return jsonify({
            'success': False,
            'message': "Editor already activated.",
        })

    editor.active = True
    db.session.commit()

    return jsonify({
        'success': True,
        'message': "Activation successful."
    })
