from flask import Flask
from flask_restful import reqparse, abort, Resource
from base64 import b64encode

artist_parser = reqparse.RequestParser()
artist_parser.add_argument('name', type=str, help='Name of artist')
artist_parser.add_argument('age', type=int, help='Age of artist')

def abort_if_artist_doesnt_exist(artist_id):
    artist_id_list = [artist.ID for artist in ArtistModel.query.all()]
    if artist_id not in artist_id_list:
        abort(404, message="Artist {} doesn't exist".format(artist_id))

# Artist
# shows a single artist item and lets you delete a artist item
class Artist(Resource):
    def get(self, artist_id):
        abort_if_artist_doesnt_exist(artist_id)
        artist = ArtistModel.query.filter(ArtistModel.ID == artist_id)
        return artist.serialize(), 200

    def delete(self, artist_id):
        abort_if_artist_doesnt_exist(artist_id)
        ArtistModel.query.filter(ArtistModel.ID == artist_id).delete()
        db.session.commit()
        return 204

# ArtistList
# shows a list of all artists, and lets you POST to add new artists
class ArtistList(Resource):
    def get(self):
        json_list = []
        for artist in ArtistModel.query.all():
            json_list.append(artist.serialize())
        return json_list, 200

    def post(self):
        args = artist_parser.parse_args()
        name = args['name']
        artist_id = b64encode(name.encode()).decode('utf-8')
        age = args['age']
        artist_id_list = [artist.ID for artist in ArtistModel.query.all()]
        if artist_id not in artist_id_list:
            new_artist = ArtistModel(ID = artist_id, name = name, age = age)
            db.session.add(new_artist)
            db.session.commit()
            return 201
        else:
            return 409
