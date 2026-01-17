# FlagDojo - クイックスタートガイド

## インストール完了！

FlagDojo CTFプラットフォームがすべてのコンポーネントと共に正常に実装されました。

## 含まれているもの

✅ **5つのチャレンジ** - すべて完全に機能し、解答可能な状態です：
- Search XSS（反射型XSS） - 簡単、100ポイント
- Comment Board（格納型XSS） - 中級、200ポイント
- Login Bypass（SQLインジェクション） - 簡単、100ポイント
- Transfer Funds（CSRF） - 中級、200ポイント
- File Viewer（パストラバーサル） - 簡単、100ポイント

✅ **コアプラットフォーム**：
- ユーザー認証システム
- 進捗トラッキングダッシュボード
- 管理画面
- Flag検証システム
- チャレンジを簡単に追加できるプラグインアーキテクチャ

✅ **ドキュメント**：
- README.md - 完全なセットアップ手順
- SECURITY.md - 重要なセキュリティ警告
- チャレンジ管理用のユーティリティスクリプト

✅ **Docker対応**：
- uvパッケージマネージャー付きDockerfile
- 簡単なデプロイ用のdocker-compose.yml

## はじめに

### オプション1: uvでローカル実行

```bash
# uvがインストールされていることを確認
uv --version

# 依存関係をインストール（初回のみ）
uv sync

# データベースは既に初期化されています！
# アプリケーションを起動するだけです
uv run python run.py
```

ブラウザで **http://localhost:5000** を開いてください

### オプション2: Dockerで実行

```bash
# ビルドして起動
docker-compose -f docker/docker-compose.yml up --build

# http://localhost:5000 でアクセス
```

### デフォルトの認証情報

- **ユーザー名**: `admin`
- **パスワード**: `changeme`

⚠️ **重要**: 初回ログイン後、管理者パスワードを変更してください！

## プロジェクト構造

```
FlagDojo/
├── app/                      # コアアプリケーション
│   ├── __init__.py          # 自動検出機能付きアプリファクトリー
│   ├── base_challenge.py    # チャレンジの基底クラス
│   ├── models.py            # データベースモデル
│   ├── config.py            # 設定
│   ├── extensions.py        # Flask拡張機能
│   ├── core/                # コアプラットフォームルート
│   │   ├── routes.py        # メインルート
│   │   ├── auth.py          # 認証
│   │   └── admin.py         # 管理画面
│   ├── static/              # 静的ファイル
│   └── templates/           # ベーステンプレート
│
├── challenges/              # すべてのチャレンジ（プラグインベース）
│   ├── xss-reflected/      # チャレンジ1
│   ├── sqli-basic/         # チャレンジ2
│   ├── xss-stored/         # チャレンジ3
│   ├── csrf-attack/        # チャレンジ4
│   └── path-traversal/     # チャレンジ5
│
├── scripts/                 # ユーティリティスクリプト
│   ├── init_db.py          # データベース初期化（✅ 実行済み！）
│   ├── add_challenge.py    # チャレンジジェネレーター
│   └── reset_progress.py   # 進捗リセットツール
│
├── docker/                  # Docker設定
│   ├── Dockerfile          # Dockerイメージ定義
│   └── docker-compose.yml  # Docker Compose設定
│
├── data/                    # データベースの場所
│   └── flagdojo.db         # SQLiteデータベース（✅ 作成済み！）
│
├── README.md               # 完全なドキュメント
├── SECURITY.md             # セキュリティガイドライン
├── pyproject.toml          # プロジェクト依存関係
└── run.py                  # 開発サーバー
```

## データベースの状態

✅ データベースが正常に初期化されました！
- 場所: `data/flagdojo.db`
- 管理者ユーザーが作成されました
- 5つのチャレンジが登録されました
- すべてのテーブルが作成されました

## 新しいチャレンジの追加

チャレンジジェネレーターを使用：

```bash
uv run python scripts/add_challenge.py \
  --slug new-challenge \
  --title "新しいチャレンジ" \
  --category XSS \
  --difficulty medium
```

または、`challenges/` に `challenge.py` ファイルを含むフォルダを手動で作成します。

## チャレンジの管理

```bash
# チャレンジを無効化（先頭に_を付ける）
mv challenges/sqli-basic challenges/_sqli-basic

# 再有効化
mv challenges/_sqli-basic challenges/sqli-basic

# 完全に削除
rm -rf challenges/old-challenge
```

## ユーティリティコマンド

```bash
# すべての進捗をリセット
uv run python scripts/reset_progress.py

# 特定のユーザーをリセット
uv run python scripts/reset_progress.py --user admin

# すべてのユーザーと進捗をリスト表示
uv run python scripts/reset_progress.py --list-users

# すべてのチャレンジをリスト表示
uv run python scripts/reset_progress.py --list-challenges
```

## 次のステップ

1. **アプリケーションを起動**: `uv run python run.py`
2. admin/changemeで**ログイン**
3. 管理画面で**パスワードを変更**
4. **チャレンジを解き始める！**

## チャレンジのテスト

各チャレンジには意図的な脆弱性があります：

1. **XSS反射型**: 検索ボックスに `<script>alert(1)</script>` を試す
2. **SQLインジェクション**: ユーザー名に `admin' --` を使用
3. **XSS格納型**: `<script>alert(1)</script>` でコメントを投稿
4. **CSRF**: ログイン中に攻撃デモページを訪問
5. **パストラバーサル**: ファイルパスに `../../../../../../tmp/secret.txt` を試す

## 重要なセキュリティ注意事項

⚠️ **このアプリケーションには意図的な脆弱性が含まれています**

- **公開インターネットにデプロイしないでください**
- **隔離されたローカル環境でのみ使用してください**
- **教育目的のみ**
- 完全なガイドラインはSECURITY.mdを参照

## サポート

- 完全なドキュメント: `README.md` を参照
- セキュリティ情報: `SECURITY.md` を参照
- 問題: 実装を確認するか、Issueを作成してください

## 機能

- チャレンジの自動検出
- プラグインアーキテクチャ（フォルダで追加・削除）
- 進捗追跡
- 管理ダッシュボード
- SQLiteデータベース（設定不要）
- Tailwind CSSのモダンUI
- Docker対応
- ゼロコスト（100%ローカル）

---

**ハッピーハッキング！**

開始: `uv run python run.py`
