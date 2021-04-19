from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_restful import reqparse, abort, Api, Resource
from base64 import b64encode

app = Flask(__name__)
db = SQLAlchemy(app)
app.config['SECRET_KEY'] = 'secret'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'

class ArtistModel(db.Model):
    ID = db.Column(db.String(80), primary_key=True)
    name = db.Column(db.String(80), unique=True, nullable=False)
    age = db.Column(db.Integer, nullable=False)
    albums = db.relationship('AlbumModel', backref='artist_model', lazy = 'dynamic')
    tracks = db.relationship('TrackModel', backref='artist_model', lazy = 'dynamic')
    
    def serialize(self):
        return {
                "id": self.ID,
                "name": self.name,
                "age": self.age,
                "albums": f"https://app-musica-t2.herokuapp.com/artists/{self.ID}/albums",
                "tracks": f"https://app-musica-t2.herokuapp.com/artists/{self.ID}/tracks",
                "self": f"https://app-musica-t2.herokuapp.com/artists/{self.ID}"
                }

class AlbumModel(db.Model):
    ID = db.Column(db.String(80), primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    genre = db.Column(db.String(80), nullable=False)
    artist_id = db.Column(db.String(80), db.ForeignKey('artist_model.ID'), nullable=False)
    songs = db.relationship('TrackModel', backref='album_model', lazy = 'dynamic')

    def serialize(self):
        return {
                "id": self.ID,
                "artist_id": self.artist_id,
                "name": self.name,
                "genre": self.genre,
                "artist": f"https://app-musica-t2.herokuapp.com/artists/{self.artist_id}",
                "tracks": f"https://app-musica-t2.herokuapp.com/albums/{self.ID}/tracks",
                "self": f"https://app-musica-t2.herokuapp.com/albums/{self.ID}"
                }

class TrackModel(db.Model):
    ID = db.Column(db.String(80), primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    duration = db.Column(db.Float, nullable=False)
    times_played = db.Column(db.Integer, nullable=False)
    album_id = db.Column(db.String(80), db.ForeignKey('album_model.ID'), nullable=False)
    artist_id = db.Column(db.String(80), db.ForeignKey('artist_model.ID'), nullable=False)
    
    def serialize(self):
        return {
                "id": self.ID,
                "album_id": self.album_id,
                "name": self.name,
                "duration": self.duration,
                "times_played": self.times_played,
                "artist": f"https://app-musica-t2.herokuapp.com/albums/{self.artist_id}",
                "album": f"https://app-musica-t2.herokuapp.com/albums/{self.album_id}",
                "self": f"https://app-musica-t2.herokuapp.com/tracks/{self.ID}"
                }   

# Artist
def abort_if_artist_doesnt_exist(artist_id):
    artist_id_list = [artist.ID for artist in ArtistModel.query.all()]
    if artist_id not in artist_id_list:
        abort(404, message="Artist {} doesn't exist".format(artist_id))

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

## setup the Api resource routing here
## endpoints
api = Api(app)
api.add_resource(ArtistList, '/artists')
api.add_resource(Artist, '/artists/<artist_id>')

#api.add_resource(album.AlbumList, '/albums')
#api.add_resource(album.Artist, '/albums/<album_id>')

#api.add_resource(album.TrackList, '/tracks')
#api.add_resource(album.Track, '/tracks/<track_id>')

if __name__ == '__main__':
    app.run(debug=True)