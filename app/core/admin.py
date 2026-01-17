"""
Admin interface routes (SECURE).
Provides basic admin functionality for managing the platform.
"""
from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from functools import wraps

from app.extensions import db
from app.models import User, Challenge, Submission, Solve

bp = Blueprint('admin', __name__, url_prefix='/admin')


def admin_required(f):
    """Decorator to require admin access."""
    @wraps(f)
    @login_required
    def decorated_function(*args, **kwargs):
        if not current_user.is_admin:
            flash('You do not have permission to access this page.', 'error')
            return redirect(url_for('core.index'))
        return f(*args, **kwargs)
    return decorated_function


@bp.route('/')
@admin_required
def index():
    """Admin dashboard."""
    # Get statistics
    total_users = User.query.count()
    total_challenges = Challenge.query.count()
    active_challenges = Challenge.query.filter_by(is_active=True).count()
    total_submissions = Submission.query.count()
    total_solves = Solve.query.count()

    # Recent submissions
    recent_submissions = Submission.query\
        .join(User)\
        .join(Challenge)\
        .order_by(Submission.submitted_at.desc())\
        .limit(20)\
        .all()

    return render_template(
        'admin/dashboard.html',
        total_users=total_users,
        total_challenges=total_challenges,
        active_challenges=active_challenges,
        total_submissions=total_submissions,
        total_solves=total_solves,
        recent_submissions=recent_submissions
    )


@bp.route('/challenges')
@admin_required
def challenges():
    """Manage challenges."""
    challenges = Challenge.query.order_by(Challenge.order, Challenge.id).all()

    # Add solve counts
    for challenge in challenges:
        challenge.solve_count = challenge.get_solve_count()
        challenge.submission_count = challenge.get_submission_count()

    return render_template('admin/challenges.html', challenges=challenges)


@bp.route('/challenge/<int:challenge_id>/toggle', methods=['POST'])
@admin_required
def toggle_challenge(challenge_id):
    """Toggle challenge active status."""
    challenge = Challenge.query.get_or_404(challenge_id)
    challenge.is_active = not challenge.is_active
    db.session.commit()

    status = 'activated' if challenge.is_active else 'deactivated'
    flash(f'Challenge "{challenge.title}" has been {status}.', 'success')
    return redirect(url_for('admin.challenges'))


@bp.route('/users')
@admin_required
def users():
    """Manage users."""
    users = User.query.all()

    # Add user statistics
    for user in users:
        user.score = user.get_score()
        user.solve_count = Solve.query.filter_by(user_id=user.id).count()

    return render_template('admin/users.html', users=users)


@bp.route('/submissions')
@admin_required
def submissions():
    """View all submissions."""
    page = request.args.get('page', 1, type=int)
    per_page = 50

    submissions_query = Submission.query\
        .join(User)\
        .join(Challenge)\
        .order_by(Submission.submitted_at.desc())

    pagination = submissions_query.paginate(page=page, per_page=per_page, error_out=False)

    return render_template(
        'admin/submissions.html',
        submissions=pagination.items,
        pagination=pagination
    )
