import sqlite3
from flask import g, current_app, jsonify

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
