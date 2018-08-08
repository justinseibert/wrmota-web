from pprint import pprint
from flask import jsonify
from wrmota import database as Database
from wrmota.api import sanitize as Sanitize
from wrmota.api import hashes as Hashes

def all_data():
    db = Database.get_db()
    data = db.execute('''
        SELECT
            address.id as address_id,
            address.address as address,
            address.lat as lat,
            address.lng as lng,
            address.artist as artist_id,
            artist.artist as artist_name,
            artist.location as artist_location,
            artist.website as artist_website,
            artist_meta.visitor as visitor_status,
            address.audio as audio_id,
            audio.directory as audio_directory,
            audio.name as audio_file,
            story.story as audio_story,
            address.theme as theme_id,
            theme.theme as theme,
            color_code.code as code
        FROM
            address
        LEFT JOIN artist on address.artist = artist.id
        LEFT JOIN artist_meta on artist.meta = artist_meta.id
        LEFT JOIN address_meta as status on address.meta = status.id
        LEFT JOIN media as audio on address.audio = audio.id
        LEFT JOIN media as story on address.story = story.id
        LEFT JOIN theme on address.theme = theme.id
        LEFT JOIN color_code on color_code.address = address.id
        WHERE status.installed = 1
        ORDER BY address.artist ASC
    ''').fetchall()

    selection = {
        'artists': 'artist_name',
        'codes': 'code',
        'addresses': 'address',
        'visitors': 'visitor_status'
    }

    result = {}
    for k,v in selection.items():
        print(v)
        result[k] = {
            'list': Database.get_list_of(v,data),
            'data': Database.get_dict_by(v,data)
        }

    return jsonify(result)

def readable_data(option):
    db = Database.get_db()
    data = db.execute('''
        SELECT
            color.code,
            address.id as id,
            address.address,
            address.brick,
            address.lat,
            address.lng,
            address.meta as address_meta_id,
            address_meta.installed,
            address.artist as artist_id,
            artist.artist,
            artist.website,
            artist.location,
            artist.meta as artist_meta_id,
            artist_meta.visitor,
            artist_meta.art_received,
            address.audio as audio_id,
            audio.directory as audio_directory,
            audio.name as audio,
            audio.original_filename as original_audio,
            audio.uploaded_by,
            address.image as image_id,
            image.directory as image_directory,
            image.name as image,
            image.original_filename as original_image,
            address.theme as theme_id,
            theme.theme as theme,
            address.story as story_id,
            story.story as story
        FROM
            address
        LEFT JOIN artist ON address.artist = artist.id
        LEFT JOIN media AS audio ON address.audio = audio.id
        LEFT JOIN media AS image ON address.image = image.id
        LEFT JOIN media AS story ON address.story = story.id
        LEFT JOIN color_code AS color ON color.address = address.id
        LEFT JOIN theme AS theme on address.theme = theme.id
        INNER JOIN artist_meta ON address.artist = artist_meta.id
        INNER JOIN address_meta ON address.meta = address_meta.id
    ''').fetchall()

    result = Database.get_dict_of(data)

    if not option or option != 'raw':
        for each in result['data']:
            each['brick'] = Sanitize.brick_as_letter(each['brick'])

            uploaded_by = Sanitize.email_sender(each['uploaded_by'])
            each['uploaded_by'] = uploaded_by['name'] if uploaded_by else each['uploaded_by']

            each['visitor'] = Sanitize.visitor_status(each['visitor'])

    return jsonify(result)

def photo_data():
    db = Database.get_db()
    data = db.execute('''
        SELECT
            color_code.code as code,
            address.id as address_id,
            address.address,
            artist.artist,
            address.image as artwork_id,
            artOriginal.id as artOriginal_id,
            artOriginal.directory as artOriginal_directory,
            artOriginal.name as artOriginal_filename,

            artInstalled1.id as artInstalled1_id,
            artInstalled1.directory as artInstalled1_directory,
            artInstalled1.name as artInstalled1_filename,

            artInstalled2.id as artInstalled2_id,
            artInstalled2.directory as artInstalled2_directory,
            artInstalled2.name as artInstalled2_filename,

            artInstalled3.id as artInstalled3_id,
            artInstalled3.directory as artInstalled3_directory,
            artInstalled3.name as artInstalled3_filename
        FROM
            address
        LEFT JOIN color_code ON color_code.address = address.id
        LEFT JOIN artist ON address.artist = artist.id
        LEFT JOIN artwork ON address.image = artwork.id
        LEFT JOIN media AS artOriginal ON artwork.original = artOriginal.id
        LEFT JOIN media AS artInstalled1 ON artwork.installed1 = artInstalled1.id
        LEFT JOIN media AS artInstalled2 ON artwork.installed2 = artInstalled2.id
        LEFT JOIN media AS artInstalled3 ON artwork.installed3 = artInstalled3.id
        WHERE address.artist IS NOT NULL
    ''').fetchall()

    result = Database.get_dict_of(data)
    return jsonify(result)

def app_uuid(device):
    hash = Hashes.store_password(device['uuid'],unique_salt=False)
    print('device uuid: {}'.format(hash['password']))
    print('user uuid  : {}'.format(hash['uuid']))
    result = {
        'uuid': hash['uuid'].decode('utf-8')
    }
    return jsonify(result)
