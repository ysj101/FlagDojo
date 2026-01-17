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
XSS攻撃に成功して、JavaScriptコードを実行させてください。
成功するとフラグが表示されます。
    '''
    flag = 'FLAG{r3fl3ct3d_xss_1s_d4ng3r0us}'
    hints = [
        '次を検索してみてください: <script>alert(1)</script>',
        '検索語がサニタイズされずにHTMLに直接反映されています',
        'ページのソースコードを見て、どこに脆弱性があるか確認してください'
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

            # Check if XSS attack was successful (contains script tag)
            show_flag = '<script>' in search_term.lower() and '</script>' in search_term.lower()

            # INTENTIONAL VULNERABILITY: No escaping!
            # In a real application, you would use {{ search_term }} in template
            # which automatically escapes. Here we use |safe to disable escaping.

            return render_template(
                'search.html',
                search_term=search_term,
                show_flag=show_flag,
                flag=self.flag if show_flag else None,
                challenge_summary=self.summary,
                challenge_description=self.description,
                challenge_hints=self.hints
            )
