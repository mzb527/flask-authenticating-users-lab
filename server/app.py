#!/usr/bin/env python3

from flask import Flask, make_response, jsonify, request, session
from flask_migrate import Migrate
from flask_restful import Api, Resource
from flask_sqlalchemy import SQLAlchemy
from models import db, User, Article, ArticlesSchema, UserSchema

# Initialize Flask app
app = Flask(__name__)
app.secret_key = b'Y\xf1Xz\x00\xad|eQ\x80t \xca\x1a\x10K'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.json.compact = False

# Initialize database and migration
db = SQLAlchemy(app)
migrate = Migrate(app, db)
api = Api(app)

# Define models
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)

class Article(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    content = db.Column(db.Text, nullable=False)

# Authentication Routes
class Login(Resource):
    def post(self):
        data = request.get_json()
        username = data.get('username')

        user = User.query.filter_by(username=username).first()

        if user:
            session['user_id'] = user.id
            return jsonify({'id': user.id, 'username': user.username}), 200

        return jsonify({'error': 'User not found'}), 404

class Logout(Resource):
    def delete(self):
        session.pop('user_id', None)
        return {}, 204

class CheckSession(Resource):
    def get(self):
        user_id = session.get('user_id')

        if user_id:
            user = User.query.get(user_id)
            return jsonify({'id': user.id, 'username': user.username}), 200

        return {}, 401

# Existing Routes
class ClearSession(Resource):
    def delete(self):
        session['page_views'] = None
        session['user_id'] = None
        return {}, 204

class IndexArticle(Resource):
    def get(self):
        articles = [{'id': article.id, 'title': article.title, 'content': article.content} for article in Article.query.all()]
        return articles, 200

class ShowArticle(Resource):
    def get(self, id):
        session['page_views'] = 0 if not session.get('page_views') else session.get('page_views')
        session['page_views'] += 1

        if session['page_views'] <= 3:
            article = Article.query.filter(Article.id == id).first()
            return jsonify({'id': article.id, 'title': article.title, 'content': article.content}), 200

        return {'message': 'Maximum pageview limit reached'}, 401

# Register resources
api.add_resource(Login, '/login')
api.add_resource(Logout, '/logout')
api.add_resource(CheckSession, '/check_session')
api.add_resource(ClearSession, '/clear')
api.add_resource(IndexArticle, '/articles')
api.add_resource(ShowArticle, '/articles/<int:id>')

# Run the app
if __name__ == '__main__':
    app.run(port=5555, debug=True)