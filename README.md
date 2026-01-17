# 🥋 FlagDojo

**Web脆弱性に特化したローカルCTF学習プラットフォーム**。安全なオフライン環境で、個人でWeb セキュリティを学習できます - 完全無料！

[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![Flask](https://img.shields.io/badge/Flask-3.0-green.svg)](https://flask.palletsprojects.com/)
[![uv](https://img.shields.io/badge/uv-パッケージマネージャー-orange.svg)](https://github.com/astral-sh/uv)

## 🎯 特徴

- **5つの組み込みチャレンジ**: XSS (反射型・格納型)、SQLインジェクション、CSRF、パストラバーサル
- **プラグインアーキテクチャ**: フォルダを作成するだけで新しいチャレンジを追加可能
- **ゼロコスト**: SQLiteを使用して完全にローカルで実行
- **モダンなUI**: Tailwind CSSで構築されたクリーンなインターフェース
- **進捗トラッキング**: 解答、提出、ポイントを追跡
- **教育的**: 各チャレンジにヒントと学習リソースを含む
- **Docker対応**: Docker Composeで簡単にデプロイ可能

## 🏗️ アーキテクチャ

```
┌─────────────────────────────────────────┐
│  Flask Application (FlagDojo)           │
├─────────────────────────────────────────┤
│  コアプラットフォーム（セキュア）        │
│  - 認証                                  │
│  - Flag検証                              │
│  - 進捗追跡                              │
│  - 管理画面                              │
├─────────────────────────────────────────┤
│  チャレンジ（意図的に脆弱）              │
│  - プラグインベースの自動検出             │
│  - 各チャレンジは独立                    │
│  - フォルダ操作で追加・削除可能           │
└─────────────────────────────────────────┘
```

## 🚀 クイックスタート

### 前提条件

- Python 3.11以上
- [uv](https://github.com/astral-sh/uv) (推奨パッケージマネージャー)

### uvを使ったインストール

```bash
# リポジトリをクローン
git clone https://github.com/yourusername/flagdojo.git
cd flagdojo

# uvをインストール（未インストールの場合）
curl -LsSf https://astral.sh/uv/install.sh | sh

# 依存関係をインストール
uv sync

# データベースを初期化
uv run python scripts/init_db.py

# アプリケーションを起動
uv run python run.py
```

### Dockerを使用

```bash
# ビルドして起動
docker-compose -f docker/docker-compose.yml up --build -d

# ログを表示
docker-compose -f docker/docker-compose.yml logs -f

# 停止
docker-compose -f docker/docker-compose.yml down
```

アプリケーションは **http://localhost:5000** でアクセス可能です

### デフォルトの認証情報

- **ユーザー名**: `admin`
- **パスワード**: `changeme`

⚠️ **初回ログイン後、必ずパスワードを変更してください！**

## 📚 組み込みチャレンジ

| # | タイトル | カテゴリ | 難易度 | ポイント | 説明 |
|---|---------|---------|--------|---------|------|
| 1 | Search XSS | 反射型XSS | 簡単 | 100 | 出力エスケープの重要性を学ぶ |
| 2 | Comment Board | 格納型XSS | 中級 | 200 | 永続的XSS攻撃を理解する |
| 3 | Login Bypass | SQLインジェクション | 簡単 | 100 | 認証バイパスを実践する |
| 4 | Transfer Funds | CSRF | 中級 | 200 | CSRFトークンの必要性を発見する |
| 5 | File Viewer | パストラバーサル | 簡単 | 100 | パス検証の重要性を学ぶ |

## 🔌 新しいチャレンジの追加（プラグインシステム）

FlagDojoは**プラグインアーキテクチャ**を採用 - チャレンジの追加はフォルダを作成するだけです！

### 方法1: ジェネレータースクリプトを使用

```bash
uv run python scripts/add_challenge.py \
  --slug my-challenge \
  --title "マイチャレンジ" \
  --category XSS \
  --difficulty medium
```

これにより、必要なファイルがすべて含まれた `challenges/my-challenge/` テンプレートが作成されます。

### 方法2: 手動作成

1. **チャレンジディレクトリを作成**:
   ```bash
   mkdir challenges/my-challenge
   mkdir challenges/my-challenge/templates
   ```

2. **`challenge.py`を作成**:
   ```python
   from flask import render_template
   from app.base_challenge import BaseChallenge

   class MyChallenge(BaseChallenge):
       slug = 'my-challenge'
       title = 'マイチャレンジ'
       category = 'XSS'
       difficulty = 'medium'
       points = 200
       description = 'チャレンジの説明をここに記載'
       flag = 'FLAG{your_flag_here}'

       def register_routes(self):
           @self.blueprint.route('/')
           def index():
               return render_template('index.html')
   ```

3. **アプリを再起動** - 新しいチャレンジが自動的に検出されて読み込まれます！

### チャレンジの管理

```bash
# チャレンジを無効化（先頭に_を付ける）
mv challenges/my-challenge challenges/_my-challenge

# 再有効化
mv challenges/_my-challenge challenges/my-challenge

# 完全に削除
rm -rf challenges/old-challenge
```

## 🗂️ プロジェクト構造

```
FlagDojo/
├── app/
│   ├── __init__.py          # チャレンジ自動検出機能付きアプリファクトリー
│   ├── base_challenge.py    # すべてのチャレンジの基底クラス
│   ├── models.py            # データベースモデル
│   ├── config.py            # 設定
│   ├── core/                # コアプラットフォーム（認証、ルート、管理画面）
│   ├── static/              # CSS、JS、画像
│   └── templates/           # ベーステンプレート
├── challenges/              # プラグインチャレンジ（自由に追加・削除可能！）
│   ├── xss-reflected/
│   ├── sqli-basic/
│   ├── xss-stored/
│   ├── csrf-attack/
│   └── path-traversal/
├── scripts/
│   ├── init_db.py          # データベース初期化
│   ├── add_challenge.py    # チャレンジジェネレーター
│   └── reset_progress.py   # 進捗リセット
├── docker/
│   ├── Dockerfile
│   └── docker-compose.yml
├── data/                   # SQLiteデータベース（自動作成）
├── pyproject.toml          # uvプロジェクト定義
└── run.py                  # 開発サーバー
```

## 🛠️ 開発

### テストの実行

```bash
# 開発用依存関係をインストール
uv sync --dev

# テストを実行
uv run pytest

# カバレッジ付き
uv run pytest --cov=app
```

### データベース管理

```bash
# データベースの初期化/リセット
uv run python scripts/init_db.py

# 進捗のリセット（ユーザーは保持）
uv run python scripts/reset_progress.py

# アプリコンテキストでPythonシェルにアクセス
uv run flask shell
```

## 🔒 セキュリティに関する注意事項

**⚠️ 重要: このアプリケーションは教育目的で意図的な脆弱性を含んでいます。**

- **公開インターネットにデプロイしないでください**
- **隔離されたローカル環境でのみ使用してください**
- チャレンジは脆弱になるように設計されています
- コアプラットフォームは安全ですが、チャレンジは安全ではありません
- 詳細は [SECURITY.md](SECURITY.md) を参照してください

## 🎓 学習パス

1. **簡単なチャレンジから始める**（XSS反射型、SQLインジェクション、パストラバーサル）
2. **中級に進む**（XSS格納型、CSRF）
3. **ヒントを読む** - エクスプロイトプロセスをガイドします
4. **自由に実験する** - ローカル環境なので、何も壊れません！
5. **解答後に解説を確認** - 修正方法を理解する

## 📖 リソース

- [OWASP Top 10](https://owasp.org/www-project-top-ten/)
- [PortSwigger Web Security Academy](https://portswigger.net/web-security)
- [HackTheBox](https://www.hackthebox.com/)
- [OWASP WebGoat](https://owasp.org/www-project-webgoat/)

## 🤝 貢献

貢献を歓迎します！方法:

1. **新しいチャレンジを追加** - `challenges/` に新しいチャレンジを含むPRを作成
2. **バグを修正** - 問題を見つけたらPRを開く
3. **ドキュメントを改善** - ドキュメントをより良くする
4. **アイデアを共有** - 提案をIssueで開く

## 📜 ライセンス

このプロジェクトはMITライセンスの下でライセンスされています - 詳細は[LICENSE](LICENSE)ファイルを参照してください。

## 🙏 謝辞

- [Flask](https://flask.palletsprojects.com/)で構築
- [Tailwind CSS](https://tailwindcss.com/)でスタイリング
- [uv](https://github.com/astral-sh/uv)によるパッケージ管理
- [DVWA](https://github.com/digininja/DVWA)、[WebGoat](https://owasp.org/www-project-webgoat/)、[HackTheBox](https://www.hackthebox.com/)にインスパイア

## 💬 サポート

- **Issues**: [GitHub Issues](https://github.com/yourusername/flagdojo/issues)
- **Discussions**: [GitHub Discussions](https://github.com/yourusername/flagdojo/discussions)
- **セキュリティ**: プラットフォーム自体の脆弱性を報告する場合は[SECURITY.md](SECURITY.md)を参照

---

**セキュリティ学習者の皆様へ、愛を込めて作成しました ❤️**

ハッピーハッキング！ 🥋🚩
