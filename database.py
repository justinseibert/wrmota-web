import sqlite3
from flask import g, current_app, jsonify
from pprint import pprint

from wrmota.api import hashes as Hash

def connect_db():
    rv = sqlite3.connect(current_app.config['DATABASE'])
    rv.row_factory = sqlite3.Row
    return rv

def get_db():
    if not hasattr(g, 'sqlite_db'):
        g.sqlite_db = connect_db()
    return g.sqlite_db

def get_map_points():
    db = get_db()

    address = db.execute('''
        SELECT
            address.id,
            address.address,
            address.brick,
            address.lat,
            address.lng,
            artist.artist,
            artist.website,
            artist_meta.art_received,
            media.directory,
            media.audio,
            media_meta.original_directory,
            media_meta.original_filename,
            media_meta.notes
        FROM
            address
        LEFT JOIN artist ON address.artist = artist.id
        INNER JOIN media ON address.media = media.id
        INNER JOIN artist_meta ON address.artist = artist_meta.id
        INNER JOIN media_meta ON address.media = media_meta.id
    ''').fetchall()

    return address

def get_artists_involved():
    db = get_db()

    visitor = db.execute('''
        SELECT DISTINCT
            artist.artist,
            artist.website,
            artist.location,
            artist_meta.curator
        FROM
            address
        INNER JOIN artist ON address.artist = artist.id
        INNER JOIN artist_meta ON artist.meta = artist_meta.id
        WHERE
            artist_meta.curator = 'kayla'
        OR
            artist_meta.curator = 'pam'
        ORDER BY artist.artist ASC
    ''').fetchall()

    local = db.execute('''
        SELECT DISTINCT
            artist.artist,
            artist.website,
            artist.location,
            artist_meta.curator
        FROM
            address
        INNER JOIN artist ON address.artist = artist.id
        INNER JOIN artist_meta ON artist.meta = artist_meta.id
        WHERE artist_meta.curator = 'mike'
        ORDER BY artist.artist ASC
    ''').fetchall()

    return {
        'visitor': visitor,
        'local': local
    }

def get_all_data():
    db = get_db()
    tables = [
        'address',
        'artist',
        'media',
        'address_meta',
        'artist_meta',
        'media_meta',
    ]
    data = {}
    for table in tables:
        statement = "SELECT * FROM {}".format(table)
        selection = db.execute(statement).fetchall()
        data[table] = {
            'name' : table,
            'data' : selection
        }
    return data

def get_dict_of(input_data, name='default', json=False):
    data = []
    head = input_data[0].keys()
    for d in input_data:
        data.append({h:d[h] for h in head})

    if json:
        data = jsonify(data)

    return {
        'name': name,
        'head': head,
        'data': data,
    }

def add_curator(data):
    db = get_db()
    secure = Hash.store_password(data['password'])
    pprint(secure)
    db.execute('''
        INSERT INTO curator (
            first_name,
            last_name,
            email,
            username,
            password,
            salt,
            uuid
        )
        VALUES (?,?,?,?,?,?,?)
    ''',
        [
            data['first_name'],
            data['last_name'],
            data['email'],
            data['username'],
            secure['password'],
            secure['salt'],
            secure['uuid']
        ]
    )
    db.commit()

def login(user,password):
    data = {
        'valid': False,
        'token': None
    }
    db = get_db()
    stored = db.execute('''
        SELECT
            username,
            password,
            salt,
            permission
        FROM curator
        WHERE username = (?)
    ''', [user]).fetchone()

    data['valid'] = Hash.check_password(stored['password'],stored['salt'],password)

    if data['valid']:
        uuid = Hash.generate_token()
        token = Hash.generate_token()
        db.execute('''
            UPDATE curator
            SET uuid = (?)
            WHERE username = (?)
        ''', [
            uuid,
            stored['username']
        ])
        db.execute('''
            INSERT OR REPLACE INTO session (
                uuid,
                token
            )
            VALUES (?,?)
        ''', [
            uuid,
            token
        ])
        data['token'] = token

    db.commit();

    return data

def get_session_permission(token):
    db = get_db()
    session = db.execute('''
        SELECT
            curator.permission
        FROM
            session
        INNER JOIN curator ON session.uuid = curator.uuid
        WHERE token = (?)
    ''', [token]).fetchone()

    return session['permission']
