#!/usr/bin/env python3
"""
Progress Reset Script
Resets user progress (submissions and solves) while preserving user accounts.

Usage:
    python scripts/reset_progress.py              # Reset all progress
    python scripts/reset_progress.py --user admin # Reset specific user only
    python scripts/reset_progress.py --challenge xss-reflected  # Reset specific challenge
"""

import argparse
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app import create_app
from app.extensions import db
from app.models import User, Challenge, Submission, Solve


def reset_all_progress():
    """Reset all submissions and solves."""
    app = create_app()

    with app.app_context():
        # Count before deletion
        submission_count = Submission.query.count()
        solve_count = Solve.query.count()

        # Delete all submissions and solves
        Submission.query.delete()
        Solve.query.delete()
        db.session.commit()

        print(f"✅ Reset complete!")
        print(f"   - Deleted {submission_count} submissions")
        print(f"   - Deleted {solve_count} solves")
        print(f"   - User accounts preserved")
        print(f"   - Challenges preserved")


def reset_user_progress(username):
    """Reset progress for a specific user."""
    app = create_app()

    with app.app_context():
        user = User.query.filter_by(username=username).first()

        if not user:
            print(f"❌ Error: User '{username}' not found")
            return False

        # Count before deletion
        submission_count = Submission.query.filter_by(user_id=user.id).count()
        solve_count = Solve.query.filter_by(user_id=user.id).count()

        # Delete user's submissions and solves
        Submission.query.filter_by(user_id=user.id).delete()
        Solve.query.filter_by(user_id=user.id).delete()
        db.session.commit()

        print(f"✅ Reset complete for user '{username}'!")
        print(f"   - Deleted {submission_count} submissions")
        print(f"   - Deleted {solve_count} solves")

        return True


def reset_challenge_progress(challenge_slug):
    """Reset progress for a specific challenge."""
    app = create_app()

    with app.app_context():
        challenge = Challenge.query.filter_by(slug=challenge_slug).first()

        if not challenge:
            print(f"❌ Error: Challenge '{challenge_slug}' not found")
            return False

        # Count before deletion
        submission_count = Submission.query.filter_by(challenge_id=challenge.id).count()
        solve_count = Solve.query.filter_by(challenge_id=challenge.id).count()

        # Delete challenge's submissions and solves
        Submission.query.filter_by(challenge_id=challenge.id).delete()
        Solve.query.filter_by(challenge_id=challenge.id).delete()
        db.session.commit()

        print(f"✅ Reset complete for challenge '{challenge.title}'!")
        print(f"   - Deleted {submission_count} submissions")
        print(f"   - Deleted {solve_count} solves")

        return True


def list_users():
    """List all users and their progress."""
    app = create_app()

    with app.app_context():
        users = User.query.all()

        if not users:
            print("No users found.")
            return

        print("\n📊 User Progress Summary:")
        print("-" * 70)
        print(f"{'Username':<20} {'Solves':<10} {'Submissions':<15} {'Score':<10}")
        print("-" * 70)

        for user in users:
            solves = Solve.query.filter_by(user_id=user.id).count()
            submissions = Submission.query.filter_by(user_id=user.id).count()
            score = user.get_score()
            print(f"{user.username:<20} {solves:<10} {submissions:<15} {score:<10}")

        print("-" * 70)


def list_challenges():
    """List all challenges and their solve counts."""
    app = create_app()

    with app.app_context():
        challenges = Challenge.query.order_by(Challenge.order).all()

        if not challenges:
            print("No challenges found.")
            return

        print("\n📋 Challenge Progress Summary:")
        print("-" * 80)
        print(f"{'Slug':<25} {'Title':<25} {'Solves':<10} {'Submissions':<15}")
        print("-" * 80)

        for challenge in challenges:
            solves = Solve.query.filter_by(challenge_id=challenge.id).count()
            submissions = Submission.query.filter_by(challenge_id=challenge.id).count()
            print(f"{challenge.slug:<25} {challenge.title:<25} {solves:<10} {submissions:<15}")

        print("-" * 80)


def confirm_action(message):
    """Ask for user confirmation."""
    response = input(f"{message} (y/N): ").strip().lower()
    return response == 'y'


def main():
    parser = argparse.ArgumentParser(
        description='Reset user progress in FlagDojo',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
Examples:
  python scripts/reset_progress.py                          # Reset all progress (with confirmation)
  python scripts/reset_progress.py --user admin             # Reset specific user
  python scripts/reset_progress.py --challenge xss-reflected # Reset specific challenge
  python scripts/reset_progress.py --list-users             # List all users
  python scripts/reset_progress.py --list-challenges        # List all challenges
  python scripts/reset_progress.py --force                  # Skip confirmation
        '''
    )

    parser.add_argument('--user', help='Reset progress for specific user')
    parser.add_argument('--challenge', help='Reset progress for specific challenge')
    parser.add_argument('--list-users', action='store_true',
                       help='List all users and their progress')
    parser.add_argument('--list-challenges', action='store_true',
                       help='List all challenges and solve counts')
    parser.add_argument('--force', action='store_true',
                       help='Skip confirmation prompt')

    args = parser.parse_args()

    # Handle list commands
    if args.list_users:
        list_users()
        return

    if args.list_challenges:
        list_challenges()
        return

    # Determine action
    if args.user:
        action_msg = f"⚠️  Reset progress for user '{args.user}'?"
        if args.force or confirm_action(action_msg):
            reset_user_progress(args.user)
        else:
            print("❌ Cancelled.")

    elif args.challenge:
        action_msg = f"⚠️  Reset progress for challenge '{args.challenge}'?"
        if args.force or confirm_action(action_msg):
            reset_challenge_progress(args.challenge)
        else:
            print("❌ Cancelled.")

    else:
        # Reset all progress
        action_msg = "⚠️  Reset ALL progress (submissions and solves)?"
        if args.force or confirm_action(action_msg):
            reset_all_progress()
        else:
            print("❌ Cancelled.")


if __name__ == '__main__':
    main()
