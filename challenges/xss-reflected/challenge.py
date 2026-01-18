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
        '検索語がページに直接表示されています。ブラウザの開発者ツール（F12）で「Search results for:」の部分のHTMLを確認してみてください',
        '検索語がサニタイズされずにHTMLとして解釈されています。HTMLタグやJavaScriptコードを含む文字列を検索してみてください',
        '例えば、<script>タグを使ってJavaScriptを実行できます。alert関数などを使ってみましょう'
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

            # Check if XSS attack was successful (detect common XSS payloads)
            search_lower = search_term.lower()
            show_flag = (
                ('<script>' in search_lower and '</script>' in search_lower) or  # <script>alert(1)</script>
                ('onerror=' in search_lower) or  # <img src=x onerror=alert(1)>
                ('onload=' in search_lower) or   # <body onload=alert(1)>
                ('onclick=' in search_lower) or  # <div onclick=alert(1)>
                ('javascript:' in search_lower)  # <a href="javascript:alert(1)">
            )

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
