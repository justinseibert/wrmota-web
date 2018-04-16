from pprint import pprint
from flask import jsonify
from wrmota import database as Database
from wrmota.api import sanitize as Sanitize

def latLng(data):
    db = Database.get_db()

    db.execute('''
        UPDATE address
        SET
            lat = ?,
            lng = ?
        WHERE id = ?
    ''', (
        data['lat'],
        data['lng'],
        data['id'],
    ))
    db.commit()
    return jsonify(data)

def story(data):
    db = Database.get_db()

    db.execute('''
        UPDATE media
        SET
            story = ?
        WHERE id = ?
    ''', (
        data['story'],
        data['story_id'],
    ))
    db.commit()

    data['message'] = 'story succesfully updated'
    return jsonify(data)


def website(data):
    db = Database.get_db()

    website = Sanitize.website(data['website'])

    db.execute('''
        UPDATE artist
        SET
            website = ?
        WHERE id = ?
    ''', (
        website,
        data['artist_id']
    ))
    db.commit()

    data['message'] = 'website succesfully updated'
    return jsonify(data)

def location(data):
    db = Database.get_db()

    db.execute('''
        UPDATE artist
        SET
            location = ?
        WHERE id = ?
    ''', (
        data['location'],
        data['artist_id']
    ))
    db.commit()

    data['message'] = 'location succesfully updated'
    return jsonify(data)
