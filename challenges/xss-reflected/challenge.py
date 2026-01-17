"""
Reflected XSS Challenge: Search Feature
INTENTIONALLY VULNERABLE - For educational purposes only
"""
from flask import request, render_template
from app.base_challenge import BaseChallenge


class XSSReflectedChallenge(BaseChallenge):
    """
    Reflected XSS challenge demonstrating unsafe output of user input.
    """

    # Challenge metadata
    slug = 'xss-reflected'
    title = 'Search XSS'
    category = 'XSS'
    difficulty = 'easy'
    points = 100
    description = '''
    This search feature directly displays your search query in the results.
    Can you inject JavaScript code and make it execute?
    
    **Objective**: Trigger an alert box with `alert(document.domain)`.
    '''
    flag = 'FLAG{r3fl3ct3d_xss_1s_d4ng3r0us}'
    hints = [
        'Try searching for: <script>alert(1)</script>',
        'The search term is reflected directly into the HTML without sanitization',
        'Once you get the alert working, submit the flag shown in the challenge description'
    ]
    order = 1

    def register_routes(self):
        """Register routes for this challenge."""

        @self.blueprint.route('/')
        def index():
            """
            VULNERABLE: Reflects user input without escaping.
            This is the vulnerability to exploit.
            """
            search_term = request.args.get('q', '')

            # INTENTIONAL VULNERABILITY: No escaping!
            # In a real application, you would use {{ search_term }} in template
            # which automatically escapes. Here we use |safe to disable escaping.

            return render_template(
                'search.html',
                search_term=search_term
            )
