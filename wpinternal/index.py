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

from flask import jsonify, Blueprint
import memcache
import twitter
from wpschema import Edit

from wpinternal.config import TWITTER
from wpinternal import db

index_views = Blueprint('index_views', __name__)

def tweet_to_html(data):
    text = data['text']
    urls = data['entities'].get('urls', [])
    users = data['entities'].get('user_mentions', [])

    for url in urls:
        i = url['indices']
        expanded_url = url['expanded_url']
        display_url = url['display_url']

        text = (
            text[:i[0]] +
            u'<a href=\'{}\'>{}</a>'.format(expanded_url,display_url) +
            text[i[1]:]
        )

    for user in users:
        i = user['indices']
        name = user['name']
        text = (
            text[:i[0]] +
            u'<a href=\'https://twitter.com/{0}\'><b>@{0}</b></a>'.format(name) +
            text[i[1]:]
        )

    return text


@index_views.route('/tweets', methods = ['GET'])
def tweets():
    mc = memcache.Client(['127.0.0.1:11211'], debug=0)

    results = mc.get('tweet_data')
    if results is None:
        t = twitter.Twitter(
            auth=twitter.OAuth(
                TWITTER['access_token_key'],
                TWITTER['access_token_secret'],
                TWITTER['consumer_key'],
                TWITTER['consumer_secret']
            )
        )

        statuses = t.statuses.user_timeline(screen_name="WavePlot")

        results = {"tweets":[tweet_to_html(s) for s in statuses[0:3]]}
        mc.set('tweet_data', results, time=(5*60))

    return jsonify(results)


@index_views.route('/changes', methods = ['GET'])
def changes():
    mc = memcache.Client(['127.0.0.1:11211'], debug=0)

    results = mc.get('changes_data')
    if results is None:
        results = db.session.query(Edit).order_by(Edit.time.desc()).limit(4).all()

        results = {
            'objects': [
                {
                    'id': edit.id,
                    'type': edit.type,
                    'time': str(edit.time),
                    'editor': edit.editor.name,
                    'waveplot': edit.waveplot_gid,
                }
                for edit in results
            ]
        }

        mc.set('changes_data', results, time=(1*60))

    return jsonify(results)
