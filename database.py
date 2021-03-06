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
            audio.directory as audio_dir,
            audio.name as audio,
            audio.original_filename as audio_orig,
            image.directory as image_dir,
            image.name as image,
            image.original_filename as image_orig
        FROM
            address
        LEFT JOIN artist ON address.artist = artist.id
        LEFT JOIN media AS audio ON address.audio = audio.id
        LEFT JOIN media AS image ON address.image = image.id
        INNER JOIN artist_meta ON address.artist = artist_meta.id
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

    return get_list_of('curator', curators)

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
        'color_code'
    ]
    if g and g.permission == 0:
        tables.append('curator')
        tables.append('session')

    data = {}
    for table in tables:
        statement = "SELECT * FROM {}".format(table)
        selection = db.execute(statement).fetchall()
        data[table] = {
            'name' : table,
            'data' : selection
        }
    return data

def get_print_map_data():
    db = get_db()

    data = db.execute('''
        SELECT
            address.id,
            color.code,
            address.address,
            address.brick,
            artist.id as artist_id,
            artist.artist,
            artist.location,
            artist_meta.id AS artist_meta_id,
            artist_meta.visitor,
            story.story
        FROM
            address
        LEFT JOIN artist ON address.artist = artist.id
        LEFT JOIN artist_meta ON artist.meta = artist_meta.id
        LEFT JOIN media as story ON address.story = story.id
        LEFT JOIN color_code AS color ON color.address = address.id
    ''').fetchall()

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

def get_dict_by(item, input_data, json=False):
    data = get_dict_of(input_data)
    data['head'].remove(item)

    result = {}
    for entry in data['data']:
        # set new key by item
        key = entry[item]
        # add list to support multiple data per key, if not already here
        result[key] = [] if key not in result else result[key]

        # populate all the data into a new dict
        info = {}
        for head in data['head']:
            info[head] = entry[head]

        # add the new dict to new results list
        result[key].append(info)

    if json:
        result = jsonify(result)

    return result

def get_list_of(item, input_data, distinct=True):
    result = []
    for row in input_data:
        result.append(row[item])

    if distinct:
        result = set(result)
    return sorted(list(result))

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
            print('LOGIN: not allowed')
            return data

        data['valid'] = Hash.check_password(stored['password'],stored['salt'],password)

        if data['valid']:
            token = Hash.generate_token(16)
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
            media.name,
            media.original_filename as 'current audio',
            media.uploaded_by as 'uploaded by'
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

def add_media(uploads):
    # TODO: MAKE THIS CONSIDER Multiple file uploads vs. Single file uploads
    try:
        db = get_db()
        db.executemany('''
            INSERT INTO media(
                directory,
                name,
                filetype,
                extension,
                original_directory,
                original_filename,
                notes,
                story,
                uploaded_by
            ) VALUES (?,?,?,?,?,?,?,?,?)
        ''', uploads)
        db.commit()
        latest_id = db.execute('''
            SELECT id
            FROM media
            ORDER BY id DESC
            LIMIT 1
        ''').fetchone()['id']
        return latest_id
    except:
        return False

def add_artwork_to_address(address_id, artwork_type, media_id):
    # determine if safe to add type into artwork table
    if not Sanitize.valid_artwork_type(artwork_type):
        return True, "ERROR: Not a valid artwork type"

    db = get_db()

    # get artwork entry from address table
    artwork = db.execute('''
        SELECT
            address.image,
            artwork.misc
        FROM address
        LEFT JOIN artwork ON address.image = artwork.id
        WHERE address.id = ?
    ''', [address_id]).fetchone()

    artwork_id = artwork['image']
    artwork_misc = ''

    if artwork['misc']:
        artwork_misc = artwork['misc']

    if artwork_misc == '' or not Sanitize.media_in_misc(media_id, artwork_misc):
        artwork_misc += '{},'.format(media_id)

    if artwork_id is None:
        # no artwork entry in address
        # insert new image in artwork by type
        db.execute('''
            INSERT INTO artwork ({}, misc)
            VALUES (?, ?)
        '''.format(artwork_type), [media_id, artwork_misc])
        db.commit()

        # get id of recent artwork addition
        artwork_id = db.execute('''
            SELECT id
            FROM artwork
            ORDER BY id DESC
            LIMIT 1
        ''').fetchone()['id']

        # associate artwork entry with address
        db.execute('''
            UPDATE address
            SET image = ?
            WHERE id = ?
        ''',[artwork_id,address_id])
        db.commit()
    else:
        # update artwork image by type at artwork_id
        db.execute('''
            UPDATE artwork
            SET {} = ?,
                misc = ?
            WHERE id = ?
        '''.format(artwork_type),[media_id,artwork_misc,artwork_id])
        db.commit()

    return False, "Image upload was successful"

def remove_image_from_artwork(artwork_id, artwork_type, replacement_id=None):
    if not Sanitize.valid_artwork_type(artwork_type):
        return True, "ERROR: Not a valid artwork type"

    try:
        db = get_db()

        db.execute('''
            UPDATE artwork
            SET {} = ?
            WHERE id = ?
        '''.format(artwork_type), [replacement_id,artwork_id])
        db.commit()
        return False, 'Image replacement was successful'
    except:
        return True, 'Image replacement failed'

def set_audio_per_code(media_file=None,code=None):
    db = get_db()

    media_file = Sanitize.make_unicode(media_file)
    code = Sanitize.make_unicode(code)

    media_id = db.execute('''
        SELECT media.id
        FROM media
        WHERE media.name = ?
    ''', [media_file]).fetchone()

    if media_id is None:
        return "ERROR: not able to find media file to update address"
    else:
        media_id = media_id['id']

    address_data = db.execute('''
        SELECT
            color_code.address as id,
            address.address as address,
            address.brick
        FROM color_code
        INNER JOIN address ON color_code.address = address.id
        WHERE color_code.code = ?
    ''', [code]).fetchone()

    if address_data is None or address_data['id'] is None:
        return "ERROR: not able to update address with supplied code"
    else:
        address_name = '{} {}'.format(address_data['address'],Sanitize.brick_as_letter(address_data['brick']))
        address_id = address_data['id']

    # add story here if updating by email (set story = media_id)
    db.execute('''
        UPDATE address
        SET
            audio = ?
        WHERE id = ?
    ''', [
        media_id,
        address_id
    ])
    db.commit()
    return "SUCCESS: {} updated with new information".format(address_name)
