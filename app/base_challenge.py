"""
Base challenge class for plugin architecture.
All challenges inherit from this class to maintain consistency.
"""
from flask import Blueprint
from pathlib import Path


class BaseChallenge:
    """
    Base class for all challenges.

    Challenges should inherit from this class and override:
    - All class attributes (slug, title, category, etc.)
    - register_routes() method
    - Optionally: setup_database() for challenge-specific tables
    """

    # Challenge metadata (MUST be overridden in subclass)
    slug = None  # URL-friendly identifier (e.g., 'xss-reflected')
    title = None  # Display title (e.g., 'Reflected XSS: Search')
    category = None  # Category (e.g., 'XSS', 'SQLi', 'CSRF')
    difficulty = None  # 'easy', 'medium', or 'hard'
    points = 0  # Points awarded for solving
    summary = None  # Short summary for challenge list (1-2 sentences)
    description = None  # Challenge description (can be markdown)
    flag = None  # Correct flag (plaintext)
    hints = []  # List of hints (optional)
    order = 0  # Display order (lower numbers appear first)

    def __init__(self, challenge_dir):
        """
        Initialize the challenge.

        Args:
            challenge_dir: Path object pointing to the challenge directory
        """
        if self.slug is None:
            raise NotImplementedError("Challenge must define 'slug' attribute")
        if self.title is None:
            raise NotImplementedError("Challenge must define 'title' attribute")
        if self.flag is None:
            raise NotImplementedError("Challenge must define 'flag' attribute")

        self.challenge_dir = Path(challenge_dir)

        # Create Flask Blueprint for this challenge
        self.blueprint = Blueprint(
            f'challenge_{self.slug}',
            __name__,
            url_prefix=f'/challenge/{self.slug}',
            template_folder=str(self.challenge_dir / 'templates'),
            static_folder=str(self.challenge_dir / 'static') if (self.challenge_dir / 'static').exists() else None
        )

        # Register routes
        self.register_routes()

    def register_routes(self):
        """
        Register Flask routes for this challenge.
        MUST be overridden by subclass.

        Example:
            @self.blueprint.route('/')
            def index():
                return render_template('index.html')
        """
        raise NotImplementedError("Challenge must implement register_routes() method")

    def check_flag(self, submitted_flag):
        """
        Check if submitted flag is correct.
        Default implementation: exact string match (case-sensitive).

        Override this method if you need custom flag validation.

        Args:
            submitted_flag: String submitted by user

        Returns:
            bool: True if flag is correct, False otherwise
        """
        return submitted_flag.strip() == self.flag.strip()

    def setup_database(self, db):
        """
        Setup challenge-specific database tables.
        Optional: Override if your challenge needs custom tables.

        Args:
            db: SQLAlchemy database instance

        Example:
            class XSSComment(db.Model):
                __tablename__ = 'xss_comments'
                id = db.Column(db.Integer, primary_key=True)
                content = db.Column(db.Text)
        """
        pass

    def get_metadata(self):
        """
        Get challenge metadata as a dictionary.
        Used for registering challenge in the database.

        Returns:
            dict: Challenge metadata
        """
        return {
            'slug': self.slug,
            'title': self.title,
            'category': self.category,
            'difficulty': self.difficulty or 'medium',
            'points': self.points or 100,
            'summary': self.summary,
            'description': self.description or 'No description provided.',
            'flag': self.flag,
            'hints': self.hints,
            'order': self.order,
            'is_active': True
        }

    def __repr__(self):
        return f'<Challenge {self.slug}: {self.title}>'
