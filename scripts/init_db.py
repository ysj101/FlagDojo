"""
Database initialization script for FlagDojo.
Run this to set up the database and create the initial admin user.
"""
import sys
from pathlib import Path

# Add parent directory to path to import app modules
sys.path.insert(0, str(Path(__file__).parent.parent))

from app import create_app
from app.extensions import db
from app.models import User
from app.config import Config


def init_database():
    """Initialize database and create admin user."""
    print("Initializing FlagDojo database...")

    # Ensure data directory exists
    project_root = Path(__file__).parent.parent
    data_dir = project_root / 'data'
    data_dir.mkdir(parents=True, exist_ok=True)
    print(f"✓ Data directory ready: {data_dir}")

    app = create_app()

    with app.app_context():
        # Create all tables
        print("Creating database tables...")
        db.create_all()
        print("✓ Database tables created")

        # Check if admin user exists
        admin_username = app.config['ADMIN_USERNAME']
        admin = User.query.filter_by(username=admin_username).first()

        if admin:
            print(f"✓ Admin user '{admin_username}' already exists")
        else:
            # Create admin user
            admin = User(username=admin_username, is_admin=True)
            admin.set_password(app.config['ADMIN_PASSWORD'])
            db.session.add(admin)
            db.session.commit()
            print(f"✓ Admin user created: {admin_username}")
            print(f"  Password: {app.config['ADMIN_PASSWORD']}")
            print("  ⚠️  Please change the admin password after first login!")

        # Display challenge count
        from app.models import Challenge
        challenge_count = Challenge.query.count()
        print(f"✓ {challenge_count} challenges registered")

        print("\n✅ Database initialization complete!")
        print(f"Database location: {app.config['SQLALCHEMY_DATABASE_URI']}")
        print(f"\nYou can now run the application with: python run.py")


if __name__ == '__main__':
    init_database()
