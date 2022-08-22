from flask import Flask, request
from flask_restx import Api, Resource
from flask_sqlalchemy import SQLAlchemy
from marshmallow import Schema, fields

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

api = Api(app)
movie_ns = api.namespace('movies')
director_ns = api.namespace('director')
genre_ns = api.namespace('genre')


class Movie(db.Model):
    __tablename__ = 'movie'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255))
    description = db.Column(db.String(255))
    trailer = db.Column(db.String(255))
    year = db.Column(db.Integer)
    rating = db.Column(db.Float)
    genre_id = db.Column(db.Integer, db.ForeignKey("genre.id"))
    genre = db.relationship("Genre")
    director_id = db.Column(db.Integer, db.ForeignKey("director.id"))
    director = db.relationship("Director")


class Director(db.Model):
    __tablename__ = 'director'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255))


class Genre(db.Model):
    __tablename__ = 'genre'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255))


class MovieSchema(Schema):
    id = fields.Int(dump_only=True)
    title = fields.Str()
    description = fields.Str()
    trailer = fields.Str()
    year = fields.Int()
    rating = fields.Float()
    genre_id = fields.Int()
    director_id = fields.Int()


class DirectorSchema(Schema):
    id = fields.Int(dump_only=True)
    name = fields.Str()


class GenreSchema(Schema):
    id = fields.Int(dump_only=True)
    name = fields.Str()


"""Единичная сереализация"""
movie_schema = MovieSchema()
director_schema = DirectorSchema()
genre_schema = GenreSchema()
"""Множественная сереализация"""
movies_schema = MovieSchema(many=True)
directors_schema = DirectorSchema(many=True)
genres_schema = GenreSchema(many=True)


def serialization(model, object) -> dict:
    dict = model.dump(object)
    return dict


def deserialization(model, object) -> dict:
    dict = model.load(object)
    return dict


@movie_ns.route('/')
class MovieSearchByDirector(Resource):
    def get(self):

        req_args = request.args

        director_id = req_args.get('director_id')

        result = serialization(movies_schema, Movie.query.all())

        if director_id is not None:
            director = serialization(director_schema, Director.query.get(director_id))
            movie = serialization(movies_schema, Movie.query.all())
            result = []
            for row in movie:
                if row["director_id"] == director["id"]:
                    result = []
                    result.append(row)

        genre_id = req_args.get('genre_id')
        if genre_id is not None:
            genre = serialization(genre_schema, Genre.query.get(genre_id))
            movie = serialization(movies_schema, Movie.query.all())
            for row in movie:
                if row["genre_id"] == genre["id"]:
                    result = []
                    result.append(row)
        if genre_id and director_id is not None:
            director = serialization(director_schema, Director.query.get(director_id))
            genre = serialization(genre_schema, Genre.query.get(genre_id))
            movie = serialization(movies_schema, Movie.query.all())
            for dir in movie:
                if dir["director_id"] and dir["genre_id"] == director["id"] and genre["id"]:
                    result.append(dir)

        return result, 200


@movie_ns.route('/')
class MovieView(Resource):

    def get(self):
        return serialization(movies_schema, Movie.query.all())

    def post(self):
        req_json = request.json
        new_movie = Movie(**req_json)
        with db.session.begin():
            db.session.add(new_movie)
            return "", 201


@movie_ns.route('/<int:uid>')
class MovieView(Resource):

    def get(self, uid: int):
        try:
            return serialization(movie_schema, Director.query.get(uid)), 200
        except Exception as e:
            return "", 404

    def put(self, uid):
        movie = Movie.query.get(uid)
        req_json = request.json
        movie.id = req_json.get("id")
        movie.title = req_json.get("title")
        movie.description = req_json.get("description")
        movie.trailer = req_json.get("trailer")
        movie.year = req_json.get("year")
        movie.rating = req_json.get("rating")
        movie.genre_id = req_json.get("genre_id")
        movie.director_id = req_json.get("director_id")
        db.session.add(movie)
        db.session.commit()
        return "", 204

    def delete(self, uid: int):
        movie = Movie.query.get(uid)
        db.session.delete(movie)
        db.session.commit()
        return "", 204


@director_ns.route('/')
class DirectorView(Resource):

    def get(self):
        return serialization(directors_schema, Director.query.all())

    def post(self):
        req_json = request.json
        new_director = Director(**req_json)
        with db.session.begin():
            db.session.add(new_director)
            return "", 201


@director_ns.route('/<int:uid>')
class DirectorView(Resource):

    def get(self, uid):
        try:
            return serialization(director_schema, Director.query.get(uid)), 200
        except Exception as e:
            return "", 404

    def put(self, uid):
        director = Director.query.get(uid)
        req_json = request.json
        director.id = req_json.get("id")
        director.name = req_json.get("name")
        db.session.add(director)
        db.session.commit()
        return "", 204

    def delete(self, uid: int):
        director = Director.query.get(uid)
        db.session.delete(director)
        db.session.commit()
        return "", 204


@genre_ns.route('/')
class GenreView(Resource):

    def get(self):
        return serialization(genres_schema, Genre.query.all())

    def post(self):
        req_json = request.json
        new_genre = Genre(**req_json)
        with db.session.begin():
            db.session.add(new_genre)
            return "", 201


@genre_ns.route('/<int:uid>')
class GenreView(Resource):

    def get(self, uid: int):
        try:
            return serialization(genre_schema, Director.query.get(uid)), 200
        except Exception as e:
            return "", 404

    def put(self, uid):
        genre = Genre.query.get(uid)
        req_json = request.json
        genre.id = req_json.get("id")
        genre.name = req_json.get("name")
        db.session.add(genre)
        db.session.commit()
        return "", 204

    def delete(self, uid: int):
        genre = Genre.query.get(uid)
        db.session.delete(genre)
        db.session.commit()
        return "", 204


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5001, debug=True)

