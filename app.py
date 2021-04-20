from flask import Flask, request
from flask_sqlalchemy import SQLAlchemy
from flask_restful import reqparse, abort, Api, Resource
from base64 import b64encode

app = Flask(__name__)
db = SQLAlchemy(app)
app.config['SECRET_KEY'] = 'secret'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'

class ArtistModel(db.Model):
    ID = db.Column(db.String(80), primary_key=True)
    name = db.Column(db.String(80), nullable=False)
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
    tracks = db.relationship('TrackModel', backref='album_model', lazy = 'dynamic')

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
                "album": f"https://app-musica-t2.herokuapp.com/albums/{self.album_id}",
                "self": f"https://app-musica-t2.herokuapp.com/tracks/{self.ID}"
                }   

# Artist
def abort_if_artist_doesnt_exist(artist_id, method):
    artist_id_list = [artist.ID for artist in ArtistModel.query.all()]
    if artist_id not in artist_id_list:
        if method != 'post':
            abort(404, message="artist doesn't exist")
        else:
            abort(422, message="artist doesn't exist")

def abort_if_album_doesnt_exist(album_id, method):
    album_id_list = [album.ID for album in AlbumModel.query.all()]
    if album_id not in album_id_list:
        if method != 'post':
            abort(404, message="album doesn't exist")
        else:
            abort(422, message="album doesn't exist")

def abort_if_track_doesnt_exist(track_id, method):
    track_id_list = [track.ID for track in TrackModel.query.all()]
    if track_id not in track_id_list:
        if method != 'post':
            abort(404, message="track doesn't exist")
        else:
            abort(422, message="track doesn't exist")

def validate_artist_args(args):
    name = args.get("name", type=str)
    age = args.get("age", type=int)
    if (name != None) and (age != None): 
        return True
    else:
        return False

def validate_album_args(args):
    name = args.get("name", default=None, type=str)
    genre = args.get("genre", default=None, type=str)
    if (name != None) and (genre != None):
        return True
    else:
        return False

def validate_track_args(args):
    name = args.get("name", default=None, type=str)
    duration = args.get("duration", default=None, type=float)
    if (name != None) and (duration != None):
        if duration > 0:
            return True
    else:
        return False

class Artist(Resource):
    def get(self, artist_id):
        abort_if_artist_doesnt_exist(artist_id, 'get')
        artist = ArtistModel.query.filter(ArtistModel.ID == artist_id).first()
        return artist.serialize(), 200

    def delete(self, artist_id):
        abort_if_artist_doesnt_exist(artist_id, 'delete')
        ArtistModel.query.filter(ArtistModel.ID == artist_id).delete()
        db.session.commit()
        return 'artist deleted', 204

class ArtistList(Resource):
    def get(self):
        json_list = []
        for artist in ArtistModel.query.all():
            json_list.append(artist.serialize())
        return json_list, 200

    def post(self):
        args = request.args
        if validate_artist_args(args):
            age = int(args['age'])
            name = args['name']
            artist_id = b64encode(name.encode()).decode('utf-8')
            artist_id_list = [artist.ID for artist in ArtistModel.query.all()]
            if artist_id not in artist_id_list:
                new_artist = ArtistModel(ID = artist_id, name = name, age = age)
                db.session.add(new_artist)
                db.session.commit()
                return 'artist created', 201
            else:
                return 'artist already exists', 409
        else:
            return 'invalid artist data', 400

class ArtistAlbum(Resource):
    def get(self, artist_id):
        abort_if_artist_doesnt_exist(artist_id, 'get')
        json_list = []
        for album in AlbumModel.query.filter(AlbumModel.artist_id == artist_id):
            json_list.append(album.serialize())
        return json_list, 200

    def post(self, artist_id):
        abort_if_artist_doesnt_exist(artist_id, 'post')
        args = request.args
        if validate_album_args(args):
            name = args['name']
            genre = args['genre']
            string = name+":"+artist_id
            album_id = b64encode(string.encode()).decode('utf-8')
            album_id_list = [album.ID for album in AlbumModel.query.filter(AlbumModel.artist_id == artist_id)]
            if album_id not in album_id_list:
                new_album = AlbumModel(ID = album_id, name = name, genre = genre, artist_id = artist_id)
                db.session.add(new_album)
                db.session.commit()
                return 'created', 201
            else:
                return 'artist has that album already', 409
        else:
            return 'invalid album input', 400

class ArtistTrack(Resource):
    def get(self, artist_id):
        abort_if_artist_doesnt_exist(artist_id, 'get')
        json_list = []
        for album in AlbumModel.query.filter(AlbumModel.artist_id == artist_id):
            album_id = album.ID
            for track in TrackModel.query.filter(TrackModel.album_id == album_id):
                json_track = track.serialize()
                json_track['artist'] = f"https://app-musica-t2.herokuapp.com/artists/{artist_id}"
                json_list.append(json_track)
        return json_list, 200

class ArtistTrackPlay(Resource):
    def put(self, artist_id):
        abort_if_artist_doesnt_exist(artist_id)
        for album in AlbumModel.query.filter(AlbumModel.artist_id == artist_id):
            album_id = album.ID
            for track in TrackModel.query.filter(TrackModel.album_id == album_id):
                track.times_played += 1
                db.session.commit()
        return "all songs from artist where played", 200
#Album
class Album(Resource):
    def get(self, album_id):
        abort_if_album_doesnt_exist(album_id, 'get')
        album = AlbumModel.query.filter(AlbumModel.ID == album_id).first()
        return album.serialize(), 200

    def delete(self, album_id):
        abort_if_album_doesnt_exist(album_id, 'delete')
        AlbumModel.query.filter(AlbumModel.ID == album_id).delete()
        db.session.commit()
        return 'album deleted', 204

class AlbumList(Resource):
    def get(self):
        json_list = []
        for album in AlbumModel.query.all():
            json_list.append(album.serialize())
        return json_list, 200

class AlbumTrack(Resource):
    def get(self, album_id):
        abort_if_album_doesnt_exist(album_id, 'get')
        json_list = []
        artist_id = AlbumModel.query.filter(AlbumModel.ID == album_id).first().artist_id
        for track in TrackModel.query.filter(TrackModel.album_id == album_id):
            json_track = track.serialize()
            json_track['artist'] = f"https://app-musica-t2.herokuapp.com/artists/{artist_id}"
            json_list.append(json_track)
        return json_list, 200

    def post(self, album_id):
        abort_if_album_doesnt_exist(album_id, 'post')
        args = request.args
        if validate_track_args(args):
            name = args['name']
            duration = float(args['duration'])
            string = name+":"+album_id
            track_id = b64encode(string.encode()).decode('utf-8')
            track_id_list = [track.ID for track in TrackModel.query.filter(TrackModel.album_id == album_id)]
            if track_id not in track_id_list:
                new_track = TrackModel(ID = track_id, name = name, duration = duration, times_played = 0, album_id = album_id)
                db.session.add(new_track)
                db.session.commit()
                return 'created', 201
            else:
                return 'album has that track already', 409
        else:
            'invalid track input', 400

class AlbumTrackPlay(Resource):
    def put(self, album_id):
        abort_if_album_doesnt_exist(album_id, 'put')
        for track in TrackModel.query.filter(TrackModel.album_id == album_id):
            track.times_played += 1
            db.session.commit()
        return "all songs from album where played", 200
            
#Track
class Track(Resource):
    def get(self, track_id):
        abort_if_track_doesnt_exist(track_id, 'get')
        track = TrackModel.query.filter(TrackModel.ID == track_id).first()
        album_id = track.album_id
        artist_id = AlbumModel.query.filter(AlbumModel.ID == album_id).first().artist_id
        json_track = track.serialize()
        json_track['artist'] = f"https://app-musica-t2.herokuapp.com/artists/{artist_id}"
        return json_track, 200

    def delete(self, track_id):
        abort_if_track_doesnt_exist(track_id, 'delete')
        TrackModel.query.filter(TrackModel.ID == track_id).delete()
        db.session.commit()
        return 'track deleted', 204

class TrackList(Resource):
    def get(self):
        json_list = []
        for track in TrackModel.query.all():
            album_id = track.album_id
            artist_id = AlbumModel.query.filter(AlbumModel.ID == album_id).first().artist_id
            json_track = track.serialize()
            json_track['artist'] = f"https://app-musica-t2.herokuapp.com/artists/{artist_id}"
            json_list.append(json_track)
        return json_list, 200

class TrackPlay(Resource):
    def put(self, track_id):
        abort_if_track_doesnt_exist(track_id, 'put')
        track = TrackModel.query.filter(TrackModel.ID == track_id).first()
        track.times_played += 1
        db.session.commit()
        return "track was played", 200

## setup the Api resource routing here
## endpoints
api = Api(app)

api.add_resource(ArtistList, '/artists')
api.add_resource(Artist, '/artists/<artist_id>')
api.add_resource(ArtistAlbum, '/artists/<artist_id>/albums')
api.add_resource(ArtistTrack, '/artists/<artist_id>/tracks')
api.add_resource(ArtistTrackPlay, '/artists/<artist_id>/albums/play')

api.add_resource(AlbumList, '/albums')
api.add_resource(Album, '/albums/<album_id>')
api.add_resource(AlbumTrack, '/albums/<album_id>/tracks')
api.add_resource(AlbumTrackPlay, '/albums/<album_id>/tracks/play')

api.add_resource(TrackList, '/tracks')
api.add_resource(Track, '/tracks/<track_id>')
api.add_resource(TrackPlay, '/tracks/<track_id>/play')

if __name__ == '__main__':
    app.run(debug=True)