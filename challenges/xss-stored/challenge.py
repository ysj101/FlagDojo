"""
Stored XSS Challenge: Comment Board
INTENTIONALLY VULNERABLE - For educational purposes only
"""
from flask import request, render_template, redirect, url_for, flash
from app.base_challenge import BaseChallenge
from app.extensions import db
from datetime import datetime


class XSSStoredChallenge(BaseChallenge):
    """
    Stored XSS challenge demonstrating persistent XSS vulnerabilities.
    """

    # Challenge metadata
    slug = 'xss-stored'
    title = 'Comment Board'
    category = 'XSS'
    difficulty = 'medium'
    points = 200
    description = '''
    A simple comment board where users can post messages.
    All comments are stored in the database and displayed to everyone.

    **Objective**: Inject JavaScript that will execute for everyone viewing the page.
    The flag will appear once you successfully trigger an XSS payload.
    '''
    flag = 'FLAG{st0r3d_xss_1s_p3rs1st3nt}'
    hints = [
        'Try posting a comment with HTML tags like <script>alert(1)</script>',
        'The comments are displayed without proper sanitization',
        'Your payload will be stored in the database and executed for all viewers',
        'Once you get an alert working, the flag is: FLAG{st0r3d_xss_1s_p3rs1st3nt}'
    ]
    order = 3

    def setup_database(self, db):
        """Create the comments table for this challenge."""

        class XSSComment(db.Model):
            """Comment model for XSS stored challenge."""
            __tablename__ = 'xss_comments'

            id = db.Column(db.Integer, primary_key=True)
            username = db.Column(db.String(80), nullable=False)
            comment = db.Column(db.Text, nullable=False)
            created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

            def __repr__(self):
                return f'<XSSComment {self.id} by {self.username}>'

        # Store reference for use in routes
        self.XSSComment = XSSComment

    def register_routes(self):
        """Register routes for this challenge."""

        @self.blueprint.route('/')
        def index():
            """
            Display the comment board.
            VULNERABLE: Comments are displayed without escaping.
            """
            # Get all comments
            comments = self.XSSComment.query.order_by(
                self.XSSComment.created_at.desc()
            ).all()

            return render_template(
                'comments.html',
                comments=comments
            )

        @self.blueprint.route('/post', methods=['POST'])
        def post_comment():
            """
            Post a new comment.
            VULNERABLE: No input validation or sanitization.
            """
            username = request.form.get('username', 'Anonymous')
            comment = request.form.get('comment', '')

            if not comment:
                flash('Comment cannot be empty!', 'danger')
                return redirect(url_for(f'challenge_{self.slug}.index'))

            # INTENTIONAL VULNERABILITY: No sanitization!
            new_comment = self.XSSComment(
                username=username,
                comment=comment  # Dangerous: stored as-is
            )

            db.session.add(new_comment)
            db.session.commit()

            flash('Comment posted successfully!', 'success')
            return redirect(url_for(f'challenge_{self.slug}.index'))

        @self.blueprint.route('/clear', methods=['POST'])
        def clear_comments():
            """Clear all comments (for testing purposes)."""
            self.XSSComment.query.delete()
            db.session.commit()
            flash('All comments cleared!', 'info')
            return redirect(url_for(f'challenge_{self.slug}.index'))
