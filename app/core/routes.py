"""
Core platform routes (SECURE).
These routes handle the main platform functionality: challenge listing,
flag submission, and user dashboard.
"""
from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify, current_app
from flask_login import login_required, current_user
from datetime import datetime
import json

from app.extensions import db
from app.models import Challenge, Submission, Solve, User

bp = Blueprint('core', __name__)


@bp.route('/')
def index():
    """Home page with challenge list."""
    # Get all active challenges, ordered by order field
    challenges = Challenge.query.filter_by(is_active=True).order_by(Challenge.order, Challenge.id).all()

    # Group challenges by category
    challenges_by_category = {}
    for challenge in challenges:
        category = challenge.category
        if category not in challenges_by_category:
            challenges_by_category[category] = []

        # Add solve status if user is logged in
        if current_user.is_authenticated:
            challenge.solved = current_user.has_solved(challenge.id)
        else:
            challenge.solved = False

        challenges_by_category[category].append(challenge)

    return render_template('index.html', challenges_by_category=challenges_by_category)


@bp.route('/challenge/<slug>')
@login_required
def challenge_detail(slug):
    """Challenge detail page."""
    challenge = Challenge.query.filter_by(slug=slug, is_active=True).first_or_404()

    # Check if user has solved this challenge
    solved = current_user.has_solved(challenge.id)

    # Parse hints from JSON
    hints = json.loads(challenge.hints) if challenge.hints else []

    # Get user's submissions for this challenge
    submissions = Submission.query.filter_by(
        user_id=current_user.id,
        challenge_id=challenge.id
    ).order_by(Submission.submitted_at.desc()).limit(5).all()

    return render_template(
        'challenge.html',
        challenge=challenge,
        solved=solved,
        hints=hints,
        submissions=submissions
    )


@bp.route('/submit_flag', methods=['POST'])
@login_required
def submit_flag():
    """
    Handle flag submission (SECURE).
    This endpoint must be secure even though challenges are vulnerable.
    """
    data = request.get_json() if request.is_json else request.form
    challenge_slug = data.get('challenge_slug')
    submitted_flag = data.get('flag', '').strip()

    if not challenge_slug or not submitted_flag:
        return jsonify({'success': False, 'message': 'Missing challenge slug or flag'}), 400

    # Get challenge
    challenge = Challenge.query.filter_by(slug=challenge_slug, is_active=True).first()
    if not challenge:
        return jsonify({'success': False, 'message': 'Challenge not found'}), 404

    # Check if already solved
    already_solved = current_user.has_solved(challenge.id)

    # Check flag
    is_correct = challenge.check_flag(submitted_flag)

    # Record submission
    submission = Submission(
        user_id=current_user.id,
        challenge_id=challenge.id,
        submitted_flag=submitted_flag,
        is_correct=is_correct,
        ip_address=request.remote_addr,
        submitted_at=datetime.utcnow()
    )
    db.session.add(submission)

    # If correct and not already solved, create solve record
    if is_correct and not already_solved:
        solve = Solve(
            user_id=current_user.id,
            challenge_id=challenge.id,
            solved_at=datetime.utcnow()
        )
        db.session.add(solve)
        db.session.commit()

        message = f'Congratulations! You solved "{challenge.title}" and earned {challenge.points} points!'
        return jsonify({
            'success': True,
            'correct': True,
            'first_solve': True,
            'message': message,
            'points': challenge.points
        })
    elif is_correct and already_solved:
        db.session.commit()
        return jsonify({
            'success': True,
            'correct': True,
            'first_solve': False,
            'message': 'You have already solved this challenge.'
        })
    else:
        db.session.commit()
        return jsonify({
            'success': True,
            'correct': False,
            'message': 'Incorrect flag. Try again!'
        })


@bp.route('/dashboard')
@login_required
def dashboard():
    """User dashboard showing progress and statistics."""
    # Get user's solves
    solves = Solve.query.filter_by(user_id=current_user.id)\
        .join(Challenge)\
        .order_by(Solve.solved_at.desc())\
        .all()

    # Calculate stats
    total_challenges = Challenge.query.filter_by(is_active=True).count()
    solved_count = len(solves)
    total_points = current_user.get_score()

    # Get recent submissions
    recent_submissions = Submission.query.filter_by(user_id=current_user.id)\
        .join(Challenge)\
        .order_by(Submission.submitted_at.desc())\
        .limit(10)\
        .all()

    # Category progress
    categories = db.session.query(Challenge.category, db.func.count(Challenge.id))\
        .filter_by(is_active=True)\
        .group_by(Challenge.category)\
        .all()

    category_progress = []
    for category, total in categories:
        solved_in_category = db.session.query(db.func.count(Solve.id))\
            .join(Challenge)\
            .filter(Challenge.category == category, Solve.user_id == current_user.id)\
            .scalar()
        category_progress.append({
            'category': category,
            'solved': solved_in_category,
            'total': total
        })

    return render_template(
        'dashboard.html',
        solves=solves,
        total_challenges=total_challenges,
        solved_count=solved_count,
        total_points=total_points,
        recent_submissions=recent_submissions,
        category_progress=category_progress
    )


@bp.route('/leaderboard')
def leaderboard():
    """Leaderboard showing top users."""
    # Get all users with their scores
    users = User.query.all()
    leaderboard_data = []

    for user in users:
        score = user.get_score()
        solved_count = Solve.query.filter_by(user_id=user.id).count()
        leaderboard_data.append({
            'username': user.username,
            'score': score,
            'solved': solved_count
        })

    # Sort by score descending
    leaderboard_data.sort(key=lambda x: (x['score'], x['solved']), reverse=True)

    return render_template('leaderboard.html', leaderboard=leaderboard_data)
