from pprint import pprint
from flask import jsonify
from wrmota import database as Database

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
            color_code.code as code
        FROM
            address
        LEFT JOIN artist on address.artist = artist.id
        LEFT JOIN artist_meta on artist.meta = artist_meta.id
        LEFT JOIN media as audio on address.audio = audio.id
        LEFT JOIN color_code on color_code.address = address.id
        WHERE address.artist IS NOT NULL
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
        result[k] = {
            'list': Database.get_list_of(v,data),
            'data': Database.get_dict_by(v,data)
        }

    return jsonify(result)
