from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_restful import reqparse, abort, Api, Resource
import artist, album, track

app = Flask(__name__)
db = SQLAlchemy(app)
app.config['SECRET_KEY'] = 'secret'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'

class ArtistModel(db.Model):
    ID = db.Column(db.String(80), primary_key=True)
    name = db.Column(db.String(80), unique=True, nullable=False)
    age = db.Column(db.Integer, nullable=False)
    albums = db.relationship('AlbumModel', backref='artist_model', lazy = 'dynamic')
    
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
    
    def serialize(self):
        return {
                "id": self.ID,
                "album_id": self.album_id,
                "name": self.name,
                "duration": self.duration,
                "times_played": self.times_played,
                "artist": f"https://app-musica-t2.herokuapp.com/albums/{self.album_id}"
                "album": f"https://app-musica-t2.herokuapp.com/albums/{self.album_id}",
                "self": f"https://app-musica-t2.herokuapp.com/tracks/{self.ID}"
                }   

## setup the Api resource routing here
## endpoints
api = Api(app)
api.add_resource(artist.ArtistList, '/artists')
api.add_resource(artist.Artist, '/artists/<artist_id>')

#api.add_resource(album.AlbumList, '/albums')
#api.add_resource(album.Artist, '/albums/<album_id>')

#api.add_resource(album.TrackList, '/tracks')
#api.add_resource(album.Track, '/tracks/<track_id>')
