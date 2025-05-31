from __future__ import with_statement
import logging
from logging.config import fileConfig
from flask import Flask, request, session, jsonify, current_app
from alembic import context
from models import User  # Ensure User model is imported

# Initialize Flask app
app = Flask(__name__)
app.secret_key = "your_secret_key_here"  # Set a secret key for session security

# Alembic config
config = context.config
fileConfig(config.config_file_name)
logger = logging.getLogger('alembic.env')

config.set_main_option(
    'sqlalchemy.url',
    str(current_app.extensions['migrate'].db.get_engine().url).replace('%', '%%')
)
target_db = current_app.extensions['migrate'].db

def get_metadata():
    return target_db.metadatas.get(None, target_db.metadata)

@app.route("/login", methods=["POST"])
def login():
    data = request.get_json()
    username = data.get("username")

    user = User.query.filter_by(username=username).first()
    if not user:
        return jsonify({"error": "User not found"}), 404

    session["user_id"] = user.id
    return jsonify({"message": f"Welcome, {user.username}!"}), 200

@app.route("/logout", methods=["DELETE"])
def logout():
    session.pop("user_id", None)
    return jsonify({"message": "Logged out successfully"}), 204

@app.route("/check_session", methods=["GET"])
def check_session():
    user_id = session.get("user_id")
    if user_id:
        user = User.query.get(user_id)
        return jsonify({"username": user.username}), 200
    return jsonify({"error": "Unauthorized"}), 401

def run_migrations_offline():
    """Run migrations in 'offline' mode."""
    url = config.get_main_option("sqlalchemy.url")
    context.configure(url=url, target_metadata=get_metadata(), literal_binds=True)

    with context.begin_transaction():
        context.run_migrations()

def run_migrations_online():
    """Run migrations in 'online' mode."""
    def process_revision_directives(context, revision, directives):
        if getattr(config.cmd_opts, 'autogenerate', False):
            script = directives[0]
            if script.upgrade_ops.is_empty():
                directives[:] = []
                logger.info('No changes in schema detected.')

    connectable = current_app.extensions['migrate'].db.get_engine()

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=get_metadata(),
            process_revision_directives=process_revision_directives,
            **current_app.extensions['migrate'].configure_args
        )

        with context.begin_transaction():
            context.run_migrations()

if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()