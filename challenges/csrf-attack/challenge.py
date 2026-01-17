"""
CSRF Challenge: Transfer Funds
INTENTIONALLY VULNERABLE - For educational purposes only
"""
from flask import request, render_template, redirect, url_for, flash, session
from app.base_challenge import BaseChallenge
from app.extensions import db
from datetime import datetime


class CSRFChallenge(BaseChallenge):
    """
    CSRF challenge demonstrating Cross-Site Request Forgery vulnerabilities.
    """

    # Challenge metadata
    slug = 'csrf-attack'
    title = 'Transfer Funds'
    category = 'CSRF'
    difficulty = 'medium'
    points = 200
    description = '''
    アカウント間で送金ができるシンプルな銀行アプリケーションです。
    このアプリケーションには適切なCSRF保護がありません。

    **目的**: 被害者のアカウントから送金を行うCSRF攻撃を作成してください。
    自動的に送金を実行する外部HTMLページを作成する必要があります。
    '''
    flag = 'FLAG{csrf_t0k3ns_4r3_1mp0rt4nt}'
    hints = [
        '送金フォームにはCSRFトークン保護がありません',
        '自動送信する隠しフォームを持つHTMLページを作成できます',
        'method="POST" の <form> とJavaScriptを使って自動送信してみてください',
        '攻撃を理解したら、フラグは: FLAG{csrf_t0k3ns_4r3_1mp0rt4nt}'
    ]
    order = 4

    def setup_database(self, db):
        """Create tables for this challenge."""

        class CSRFAccount(db.Model):
            """Account model for CSRF challenge."""
            __tablename__ = 'csrf_accounts'

            id = db.Column(db.Integer, primary_key=True)
            username = db.Column(db.String(80), unique=True, nullable=False)
            balance = db.Column(db.Integer, nullable=False, default=1000)

            def __repr__(self):
                return f'<CSRFAccount {self.username}: ${self.balance}>'

        class CSRFTransaction(db.Model):
            """Transaction history for CSRF challenge."""
            __tablename__ = 'csrf_transactions'

            id = db.Column(db.Integer, primary_key=True)
            from_account = db.Column(db.String(80), nullable=False)
            to_account = db.Column(db.String(80), nullable=False)
            amount = db.Column(db.Integer, nullable=False)
            created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

            def __repr__(self):
                return f'<Transaction ${self.amount} from {self.from_account} to {self.to_account}>'

        # Store references
        self.CSRFAccount = CSRFAccount
        self.CSRFTransaction = CSRFTransaction

        # Initialize default accounts
        db.session.commit()

    def _init_accounts(self):
        """Initialize demo accounts if they don't exist."""
        accounts = ['alice', 'bob', 'attacker']
        for username in accounts:
            if not self.CSRFAccount.query.filter_by(username=username).first():
                account = self.CSRFAccount(username=username, balance=1000)
                db.session.add(account)
        db.session.commit()

    def register_routes(self):
        """Register routes for this challenge."""

        @self.blueprint.route('/')
        def index():
            """Main banking page."""
            # Initialize accounts
            self._init_accounts()

            # Get current user from session (default to 'alice')
            current_user = session.get(f'{self.slug}_user', 'alice')
            session[f'{self.slug}_user'] = current_user

            # Get account info
            account = self.CSRFAccount.query.filter_by(username=current_user).first()
            accounts = self.CSRFAccount.query.all()

            # Get recent transactions
            transactions = self.CSRFTransaction.query.filter(
                (self.CSRFTransaction.from_account == current_user) |
                (self.CSRFTransaction.to_account == current_user)
            ).order_by(self.CSRFTransaction.created_at.desc()).limit(10).all()

            return render_template(
                'bank.html',
                current_user=current_user,
                account=account,
                accounts=accounts,
                transactions=transactions
            )

        @self.blueprint.route('/transfer', methods=['POST'])
        def transfer():
            """
            Transfer funds between accounts.
            VULNERABLE: No CSRF token validation!
            """
            current_user = session.get(f'{self.slug}_user', 'alice')

            to_account = request.form.get('to_account')
            amount = request.form.get('amount', type=int)

            if not to_account or not amount:
                flash('Missing required fields!', 'danger')
                return redirect(url_for(f'challenge_{self.slug}.index'))

            if amount <= 0:
                flash('Amount must be positive!', 'danger')
                return redirect(url_for(f'challenge_{self.slug}.index'))

            # Get accounts
            from_acc = self.CSRFAccount.query.filter_by(username=current_user).first()
            to_acc = self.CSRFAccount.query.filter_by(username=to_account).first()

            if not to_acc:
                flash('Recipient account not found!', 'danger')
                return redirect(url_for(f'challenge_{self.slug}.index'))

            if from_acc.balance < amount:
                flash('Insufficient funds!', 'danger')
                return redirect(url_for(f'challenge_{self.slug}.index'))

            # VULNERABLE: No CSRF protection - any POST request will work!
            # Perform transfer
            from_acc.balance -= amount
            to_acc.balance += amount

            # Record transaction
            transaction = self.CSRFTransaction(
                from_account=current_user,
                to_account=to_account,
                amount=amount
            )
            db.session.add(transaction)
            db.session.commit()

            flash(f'Successfully transferred ${amount} to {to_account}!', 'success')
            return redirect(url_for(f'challenge_{self.slug}.index'))

        @self.blueprint.route('/switch/<username>')
        def switch_user(username):
            """Switch to a different user (for testing)."""
            if self.CSRFAccount.query.filter_by(username=username).first():
                session[f'{self.slug}_user'] = username
                flash(f'Switched to user: {username}', 'info')
            else:
                flash('User not found!', 'danger')
            return redirect(url_for(f'challenge_{self.slug}.index'))

        @self.blueprint.route('/reset', methods=['POST'])
        def reset():
            """Reset all accounts to default balances."""
            accounts = self.CSRFAccount.query.all()
            for account in accounts:
                account.balance = 1000

            self.CSRFTransaction.query.delete()
            db.session.commit()

            flash('All accounts reset to $1000!', 'info')
            return redirect(url_for(f'challenge_{self.slug}.index'))

        @self.blueprint.route('/attack-demo')
        def attack_demo():
            """Show example CSRF attack page."""
            return render_template('csrf_attack_demo.html')
