"""
SQL Injection Challenge: Login Bypass
INTENTIONALLY VULNERABLE - For educational purposes only
"""
from flask import request, render_template, session
from app.base_challenge import BaseChallenge
from app.extensions import db


class SQLiBasicChallenge(BaseChallenge):
    """
    SQL Injection challenge demonstrating authentication bypass.
    """

    # Challenge metadata
    slug = 'sqli-basic'
    title = 'Login Bypass'
    category = 'SQL Injection'
    difficulty = 'easy'
    points = 100
    summary = 'SQLインジェクションを使用してパスワードなしでログイン認証をバイパスします。'
    description = '''データベースに対して認証情報をチェックするシンプルなログインフォームです。
管理者のパスワードは不明ですが、認証をバイパスできるかもしれません？

**目的**:
パスワードを知らずに 'admin' ユーザーとしてログインしてください。
    '''
    flag = 'FLAG{sql_1nj3ct10n_byp4ss}'
    hints = [
        "次を入力してみてください: admin' --",
        "SQLクエリは次のような形式かもしれません: SELECT * FROM users WHERE username='...' AND password='...'",
        "SQLコメントを使用してクエリの残りを無視できます"
    ]
    order = 2

    def setup_database(self, db):
        """Setup the vulnerable user table."""
        
        class SQLiUser(db.Model):
            __tablename__ = 'sqli_users'
            id = db.Column(db.Integer, primary_key=True)
            username = db.Column(db.String(80), unique=True, nullable=False)
            password = db.Column(db.String(255), nullable=False)
            is_admin = db.Column(db.Boolean, default=False)

        # Store the model for later use
        self.SQLiUser = SQLiUser

    def register_routes(self):
        """Register routes for this challenge."""

        @self.blueprint.route('/')
        def index():
            """Login page."""
            return render_template('login.html', message=session.pop('message', None))

        @self.blueprint.route('/login', methods=['POST'])
        def login():
            """
            VULNERABLE: Uses string formatting for SQL query.
            This allows SQL injection attacks.
            """
            username = request.form.get('username', '')
            password = request.form.get('password', '')

            # INTENTIONAL VULNERABILITY: SQL Injection
            # Never do this in real code!
            query = f"SELECT * FROM sqli_users WHERE username='{username}' AND password='{password}'"

            try:
                result = db.session.execute(db.text(query)).fetchone()

                if result:
                    session['message'] = f'Success! Welcome {username}! The flag is: {self.flag}'
                    session['logged_in'] = True
                    session['username'] = username
                else:
                    session['message'] = 'Invalid username or password'
            except Exception as e:
                session['message'] = f'Error: {str(e)}'

            return render_template('login.html', message=session.get('message'))

        @self.blueprint.route('/reset', methods=['POST'])
        def reset():
            """Reset the database."""
            # Drop and recreate table
            db.session.execute(db.text('DROP TABLE IF EXISTS sqli_users'))
            db.session.commit()
            
            # Recreate table
            db.session.execute(db.text('''
                CREATE TABLE sqli_users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username VARCHAR(80) UNIQUE NOT NULL,
                    password VARCHAR(255) NOT NULL,
                    is_admin BOOLEAN DEFAULT 0
                )
            '''))
            
            # Insert sample data
            db.session.execute(db.text(
                "INSERT INTO sqli_users (username, password, is_admin) VALUES ('admin', 'super_secret_password_12345', 1)"
            ))
            db.session.execute(db.text(
                "INSERT INTO sqli_users (username, password, is_admin) VALUES ('user', 'password123', 0)"
            ))
            db.session.commit()
            
            session['message'] = 'Database reset successful'
            return render_template('login.html', message=session.get('message'))
