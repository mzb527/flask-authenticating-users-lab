from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import MetaData
from marshmallow import Schema, fields

# Define metadata with naming conventions
metadata = MetaData(naming_convention={
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
})

# Initialize database
db = SQLAlchemy(metadata=metadata)

# Define User model
class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String, unique=True, nullable=False)

    articles = db.relationship('Article', backref='user')

    def __repr__(self):
        return f'User {self.username}, ID {self.id}'

# Define Article model
class Article(db.Model):
    __tablename__ = 'articles'

    id = db.Column(db.Integer, primary_key=True)
    author = db.Column(db.String)
    title = db.Column(db.String)
    content = db.Column(db.String)
    preview = db.Column(db.String)
    minutes_to_read = db.Column(db.Integer)
    date = db.Column(db.DateTime, server_default=db.func.now())

    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))

    def __repr__(self):
        return f'Article {self.id} by {self.author}'

# Define Marshmallow Schemas
class UserSchema(Schema):
    id = fields.Int()
    username = fields.String()
    articles = fields.List(fields.Nested(lambda: ArticlesSchema(exclude=("user",))))

class ArticlesSchema(Schema):
    id = fields.Int()
    author = fields.String()
    title = fields.String()
    content = fields.String()
    preview = fields.String()
    minutes_to_read = fields.Int()
    date = fields.DateTime()
    user = fields.Nested(UserSchema(exclude=("articles",)))