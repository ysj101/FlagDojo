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
    summary = '検索機能にJavaScriptコードを注入して実行させる反射型XSSの脆弱性を学びます。'
    description = '''この検索機能は、検索クエリを結果に直接表示します。
JavaScriptコードを注入して実行させることができますか？

**目的**:
`alert(document.domain)` でアラートボックスを表示させてください。
    '''
    flag = 'FLAG{r3fl3ct3d_xss_1s_d4ng3r0us}'
    hints = [
        '次を検索してみてください: <script>alert(1)</script>',
        '検索語がサニタイズされずにHTMLに直接反映されています',
        'アラートが動作したら、チャレンジ説明に表示されているフラグを提出してください'
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
