"""
Database models for FlagDojo platform.
These models represent the core platform data structures (SECURE).
"""
from datetime import datetime
from flask_login import UserMixin
import bcrypt
from app.extensions import db


class User(UserMixin, db.Model):
    """User model for authentication and progress tracking."""
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    is_admin = db.Column(db.Boolean, default=False, nullable=False)

    # Relationships
    submissions = db.relationship('Submission', backref='user', lazy='dynamic', cascade='all, delete-orphan')
    solves = db.relationship('Solve', backref='user', lazy='dynamic', cascade='all, delete-orphan')

    def set_password(self, password):
        """Hash and set the user's password."""
        self.password_hash = bcrypt.hashpw(
            password.encode('utf-8'),
            bcrypt.gensalt()
        ).decode('utf-8')

    def check_password(self, password):
        """Verify the user's password."""
        return bcrypt.checkpw(
            password.encode('utf-8'),
            self.password_hash.encode('utf-8')
        )

    def get_score(self):
        """Calculate total points from solved challenges."""
        return db.session.query(db.func.sum(Challenge.points))\
            .join(Solve)\
            .filter(Solve.user_id == self.id)\
            .scalar() or 0

    def has_solved(self, challenge_id):
        """Check if user has solved a specific challenge."""
        return Solve.query.filter_by(
            user_id=self.id,
            challenge_id=challenge_id
        ).first() is not None

    def __repr__(self):
        return f'<User {self.username}>'


class Challenge(db.Model):
    """Challenge metadata model."""
    __tablename__ = 'challenges'

    id = db.Column(db.Integer, primary_key=True)
    slug = db.Column(db.String(100), unique=True, nullable=False, index=True)
    title = db.Column(db.String(200), nullable=False)
    category = db.Column(db.String(50), nullable=False, index=True)
    difficulty = db.Column(db.String(20), nullable=False)  # easy, medium, hard
    points = db.Column(db.Integer, nullable=False, default=100)
    description = db.Column(db.Text, nullable=False)
    flag = db.Column(db.String(255), nullable=False)  # Store plaintext flag
    hints = db.Column(db.Text)  # JSON string for hints
    order = db.Column(db.Integer, nullable=False, default=0)
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    # Relationships
    submissions = db.relationship('Submission', backref='challenge', lazy='dynamic', cascade='all, delete-orphan')
    solves = db.relationship('Solve', backref='challenge', lazy='dynamic', cascade='all, delete-orphan')

    def get_solve_count(self):
        """Get number of users who solved this challenge."""
        return Solve.query.filter_by(challenge_id=self.id).count()

    def get_submission_count(self):
        """Get total number of submissions for this challenge."""
        return Submission.query.filter_by(challenge_id=self.id).count()

    def check_flag(self, submitted_flag):
        """Check if submitted flag is correct."""
        return submitted_flag.strip() == self.flag.strip()

    def __repr__(self):
        return f'<Challenge {self.slug}>'


class Submission(db.Model):
    """Flag submission history."""
    __tablename__ = 'submissions'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    challenge_id = db.Column(db.Integer, db.ForeignKey('challenges.id'), nullable=False, index=True)
    submitted_flag = db.Column(db.String(255), nullable=False)
    is_correct = db.Column(db.Boolean, nullable=False)
    ip_address = db.Column(db.String(45))  # Support both IPv4 and IPv6
    submitted_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, index=True)

    def __repr__(self):
        return f'<Submission user={self.user_id} challenge={self.challenge_id} correct={self.is_correct}>'


class Solve(db.Model):
    """Successful challenge completions (one per user per challenge)."""
    __tablename__ = 'solves'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    challenge_id = db.Column(db.Integer, db.ForeignKey('challenges.id'), nullable=False, index=True)
    solved_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, index=True)

    # Unique constraint: one solve per user per challenge
    __table_args__ = (
        db.UniqueConstraint('user_id', 'challenge_id', name='unique_user_challenge_solve'),
    )

    def __repr__(self):
        return f'<Solve user={self.user_id} challenge={self.challenge_id}>'
