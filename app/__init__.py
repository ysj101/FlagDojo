"""
Flask application factory with plugin-based challenge loading.
This is the heart of FlagDojo - it discovers and loads challenges automatically.
"""
import sys
from pathlib import Path
from flask import Flask
import importlib.util
import json

from app.config import get_config
from app.extensions import db, login_manager
from app.models import User, Challenge
from app.base_challenge import BaseChallenge


def create_app(config_name=None):
    """
    Create and configure the Flask application.

    Args:
        config_name: Configuration name ('development', 'production', 'testing')

    Returns:
        Flask application instance
    """
    app = Flask(__name__)

    # Load configuration
    if config_name:
        app.config.from_object(f'app.config.{config_name.title()}Config')
    else:
        app.config.from_object(get_config())

    # Initialize extensions
    db.init_app(app)
    login_manager.init_app(app)

    # User loader for Flask-Login
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    # Register core blueprints
    from app.core import routes as core_routes
    from app.core import auth as core_auth
    from app.core import admin as core_admin

    app.register_blueprint(core_routes.bp)
    app.register_blueprint(core_auth.bp)
    app.register_blueprint(core_admin.bp)

    # Discover and register challenges
    with app.app_context():
        challenges = discover_challenges(app)
        app.challenges = challenges  # Store for later use

        # Create database tables
        db.create_all()

        # Sync challenges to database
        sync_challenges_to_db(challenges)

    # Register error handlers
    register_error_handlers(app)

    return app


def discover_challenges(app):
    """
    Automatically discover and load challenges from the challenges/ directory.

    This is the core of the plugin architecture:
    1. Scan challenges/ directory
    2. Find challenge.py files
    3. Import challenge classes that inherit from BaseChallenge
    4. Instantiate and register them

    Args:
        app: Flask application instance

    Returns:
        list: List of instantiated challenge objects
    """
    challenges = []
    challenges_dir = Path(app.config['CHALLENGES_DIR'])

    app.logger.info(f"Scanning for challenges in: {challenges_dir}")

    if not challenges_dir.exists():
        app.logger.warning(f"Challenges directory not found: {challenges_dir}")
        challenges_dir.mkdir(parents=True, exist_ok=True)
        return challenges

    # Iterate through challenge directories
    for challenge_path in sorted(challenges_dir.iterdir()):
        # Skip non-directories and disabled challenges (starting with _)
        if not challenge_path.is_dir() or challenge_path.name.startswith('_'):
            continue

        challenge_file = challenge_path / 'challenge.py'
        if not challenge_file.exists():
            app.logger.warning(f"No challenge.py found in {challenge_path.name}, skipping")
            continue

        try:
            # Dynamic import of challenge module
            spec = importlib.util.spec_from_file_location(
                f"challenge_{challenge_path.name}",
                challenge_file
            )
            module = importlib.util.module_from_spec(spec)
            sys.modules[spec.name] = module
            spec.loader.exec_module(module)

            # Find challenge class (must inherit from BaseChallenge)
            challenge_class = None
            for attr_name in dir(module):
                attr = getattr(module, attr_name)
                if (isinstance(attr, type) and
                    issubclass(attr, BaseChallenge) and
                    attr is not BaseChallenge):
                    challenge_class = attr
                    break

            if challenge_class is None:
                app.logger.warning(
                    f"No BaseChallenge subclass found in {challenge_path.name}/challenge.py"
                )
                continue

            # Instantiate challenge
            challenge_instance = challenge_class(challenge_path)

            # Setup challenge-specific database tables
            challenge_instance.setup_database(db)

            # Register challenge blueprint
            app.register_blueprint(challenge_instance.blueprint)

            challenges.append(challenge_instance)
            app.logger.info(f"✓ Loaded challenge: {challenge_instance.slug}")

        except Exception as e:
            app.logger.error(f"Failed to load challenge from {challenge_path.name}: {e}")
            continue

    app.logger.info(f"Total challenges loaded: {len(challenges)}")
    return challenges


def sync_challenges_to_db(challenges):
    """
    Synchronize loaded challenges to the database.
    Creates or updates Challenge records based on challenge metadata.

    Args:
        challenges: List of challenge instances
    """
    for challenge_instance in challenges:
        metadata = challenge_instance.get_metadata()

        # Check if challenge exists
        challenge = Challenge.query.filter_by(slug=metadata['slug']).first()

        if challenge:
            # Update existing challenge
            challenge.title = metadata['title']
            challenge.category = metadata['category']
            challenge.difficulty = metadata['difficulty']
            challenge.points = metadata['points']
            challenge.summary = metadata['summary']
            challenge.description = metadata['description']
            challenge.flag = metadata['flag']
            challenge.hints = json.dumps(metadata['hints']) if metadata['hints'] else None
            challenge.order = metadata['order']
            challenge.is_active = metadata['is_active']
        else:
            # Create new challenge
            challenge = Challenge(
                slug=metadata['slug'],
                title=metadata['title'],
                category=metadata['category'],
                difficulty=metadata['difficulty'],
                points=metadata['points'],
                summary=metadata['summary'],
                description=metadata['description'],
                flag=metadata['flag'],
                hints=json.dumps(metadata['hints']) if metadata['hints'] else None,
                order=metadata['order'],
                is_active=metadata['is_active']
            )
            db.session.add(challenge)

    db.session.commit()


def register_error_handlers(app):
    """Register error handlers for common HTTP errors."""

    @app.errorhandler(404)
    def not_found_error(error):
        from flask import render_template
        return render_template('errors/404.html'), 404

    @app.errorhandler(500)
    def internal_error(error):
        from flask import render_template
        db.session.rollback()
        return render_template('errors/500.html'), 500

    @app.errorhandler(403)
    def forbidden_error(error):
        from flask import render_template
        return render_template('errors/403.html'), 403
