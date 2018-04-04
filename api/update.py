from pprint import pprint
from flask import jsonify
from wrmota import database as Database

def latLng(data):
    pprint(data)
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
