from wrmota import database as Database

def essential_data():
    db = Database.get_db()
    artists = db.execute('''
        SELECT
            address.id as address_id,
            address.address,
            address.lat,
            address.lng,
            address.artist as artist_id,
            artist.artist,
            artist.location,
            artist.website,
            address.audio as media_id,
            media.directory,
            media.name
        FROM
            address
        LEFT JOIN artist on address.artist = artist.id
        LEFT JOIN media on address.audio = media.id
        WHERE address.artist IS NOT NULL
    ''').fetchall()

    data = Database.get_dict_of(artists, json=True)
    return data['data']
