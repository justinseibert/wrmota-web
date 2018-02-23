import sqlite3
from flask import g, current_app, jsonify
from pprint import pprint

from wrmota.api import hashes as Hash
from wrmota.api import sanitize as Sanitize

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
            media.file,
            media_meta.original_directory,
            media_meta.original_filename,
            media_meta.notes
        FROM
            address
        LEFT JOIN artist ON address.artist = artist.id
        INNER JOIN media ON address.audio = media.id
        INNER JOIN artist_meta ON address.artist = artist_meta.id
        INNER JOIN media_meta ON media.id = media_meta.id
    ''').fetchall()

    return address

def get_artists_involved():
    db = get_db()
    sql = '''
        SELECT
            artist.artist,
            artist.website,
            artist.location,
            artist_meta.curator
        FROM
            artist
        INNER JOIN artist_meta ON artist.meta = artist_meta.id
        WHERE artist_meta.visitor = (?)
        AND artist_meta.confirmed = 1
        ORDER BY artist.artist ASC
    '''

    visitor = db.execute(sql,[1]).fetchall()
    local = db.execute(sql,[0]).fetchall()

    return {
        'visitor': visitor,
        'local': local
    }

def get_curators_list():
    db = get_db()
    curators = db.execute('''
        SELECT DISTINCT
            curator
        FROM
            artist_meta
    ''').fetchall()

    return get_list_of(curators)

def get_data_artist():
    db = get_db()

    artist = db.execute('''
        SELECT
            artist.id,
            artist.artist,
            artist.location,
            artist.website,
            artist.bio,
            artist_meta.id AS artist_meta_id,
            artist_meta.curator,
            artist_meta.email,
            artist_meta.visitor,
            artist_meta.confirmed,
            artist_meta.assigned,
            artist_meta.info_sent,
            artist_meta.touched_base,
            artist_meta.art_received,
            artist_meta.notes
        FROM
            artist
        LEFT JOIN artist_meta ON artist.meta = artist_meta.id
    ''').fetchall()

    return artist

def get_all_data():
    db = get_db()
    tables = [
        'address',
        'artist',
        'media',
        'address_meta',
        'artist_meta',
        'media_meta',
        'curator',
        'session'
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

def get_list_of(input_data):
    output_data = []
    for row in input_data:
        output_data.append(row[0])

    return output_data

def keep_cols_in_dict(input_dict,cols):
    output_dict = {
        'name': input_dict['name'],
        'head': cols,
        'data': []
    }
    for original_row in input_dict['data']:
        revised_row = {}
        for col in cols:
            revised_row[col] = original_row[col]

        output_dict['data'].append(revised_row)

    return output_dict

def remove_cols_from_dict(input_dict,cols):
    for row in input_dict['data']:
        for col in rm_cols:
            del row[col]

    for col in rm_cols:
        input_dict['head'].remove(col)

    return input_dict

def add_curator(data):
    db = get_db()
    secure = Hash.store_password(data['password'])
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

def update_artist_data(form):
    d = {}
    for field in form:
        if field.data == True:
            v = 1
        elif field.data == False:
            v = 0
        else:
            if field.name == 'website':
                v = Sanitize.website(field.data)
            else:
                v = Sanitize.spaces(field.data)
        d[field.name] = v

    db = get_db()
    print('Update ARTIST:')
    pprint(d)
    try:
        db.execute('''
            UPDATE artist
            SET
                artist = ?,
                location = ?,
                website = ?
            WHERE id = ?
        ''', (
            d['artist'],
            d['location'],
            d['website'],
            d['artist_id']
        ))
        db.execute('''
            UPDATE artist_meta
            SET
                curator = ?,
                email = ?,
                visitor = ?,
                confirmed = ?,
                assigned = ?,
                info_sent = ?,
                touched_base = ?,
                art_received = ?
            WHERE id = ?
        ''', (
            d['curator'],
            d['email'],
            d['visitor'],
            d['confirmed'],
            d['assigned'],
            d['info_sent'],
            d['touched_base'],
            d['art_received'],
            d['artist_meta_id']
        ))
        db.commit()
        return True
    except:
        print('ERROR: artist update failed')
        return False

def login(user,password):
    data = {
        'valid': False,
        'token': None
    }
    db = get_db()
    stored = db.execute('''
        SELECT
            password,
            salt,
            permission,
            uuid
        FROM curator
        WHERE username = (?)
    ''', [user]).fetchone()

    try:
        if stored['permission'] > 10:
            print('LOGIN: invalid permission')
            return data

        data['valid'] = Hash.check_password(stored['password'],stored['salt'],password)

        if data['valid']:
            token = Hash.generate_token()
            db.execute('''
                INSERT OR REPLACE INTO session (
                    uuid,
                    token
                )
                VALUES (?,?)
            ''', [
                stored['uuid'],
                token
            ])
            data['token'] = token
    except TypeError:
        print('LOGIN: invalid credentials')

    db.commit();

    return data

def get_session_permission(token):
    db = get_db()
    user = db.execute('''
        SELECT
            curator.permission,
            curator.username
        FROM
            session
        INNER JOIN curator ON session.uuid = curator.uuid
        WHERE token = (?)
    ''', [token]).fetchone()

    g.user = user['username']
    return user['permission']

def get_address_codes():
    db = get_db()
    codes = db.execute('''
        SELECT
            address.id,
            color_code.code,
            address.address,
            address.brick,
            artist.artist,
            artist_meta.art_received,
            address_meta.installed,
            media.directory,
            media.file
        FROM
            address
        LEFT JOIN artist on address.artist = artist.id
        LEFT JOIN media on address.audio = media.id
        LEFT JOIN color_code on address.id = color_code.address
        LEFT JOIN artist_meta on artist.meta = artist_meta.id
        LEFT JOIN address_meta on address.meta = address_meta.id
    ''').fetchall()

    return codes

def get_color_code_positions():
    db = get_db()
    codes = db.execute('''
        SELECT
            id,
            p0,
            p1,
            p2,
            p3
        FROM
            color_code
        WHERE
            address is not Null
    ''').fetchall()

    return codes
