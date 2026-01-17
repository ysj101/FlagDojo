"""
Path Traversal Challenge: File Viewer
INTENTIONALLY VULNERABLE - For educational purposes only
"""
import os
from pathlib import Path
from flask import request, render_template, flash, abort
from app.base_challenge import BaseChallenge


class PathTraversalChallenge(BaseChallenge):
    """
    Path Traversal challenge demonstrating directory traversal vulnerabilities.
    """

    # Challenge metadata
    slug = 'path-traversal'
    title = 'File Viewer'
    category = 'Path Traversal'
    difficulty = 'easy'
    points = 100
    summary = 'ディレクトリトラバーサルを使用してアクセス制限外のファイルを読み取ります。'
    description = '''documentsディレクトリからテキストファイルを表示するシンプルなファイルビューアーアプリケーションです。
ドロップダウンメニューからファイルを選択して内容を表示できます。

**目的**:
パストラバーサルを使用して、documentsディレクトリ外の秘密ファイルを読み取ってください。
フラグが含まれている `/tmp/secret.txt` を見つけて読み取ってください。
    '''
    flag = 'FLAG{p4th_tr4v3rs4l_1s_d4ng3r0us}'
    hints = [
        'filenameパラメータが適切に検証されていません',
        '../ を使用してディレクトリを上に移動してみてください',
        '秘密ファイルの場所: ../../../../../../tmp/secret.txt',
        '必要に応じてURLエンコードしてください: ../ は %2e%2e%2f'
    ]
    order = 5

    def __init__(self, challenge_dir):
        """Initialize the challenge and create sample files."""
        super().__init__(challenge_dir)

        # Create documents directory
        self.docs_dir = challenge_dir / 'documents'
        self.docs_dir.mkdir(exist_ok=True)

        # Create sample documents
        self._create_sample_files()

        # Create secret file (flag location)
        self._create_secret_file()

    def _create_sample_files(self):
        """Create sample files in the documents directory."""
        files = {
            'welcome.txt': '''Welcome to FileViewer Pro!

This application allows you to view text files stored in our secure document storage.

Select a file from the dropdown menu to view its contents.

Thank you for using FileViewer Pro!
''',
            'about.txt': '''About FileViewer Pro

Version: 1.0.0
Developer: SecureCorp Inc.
License: Proprietary

This software is provided as-is without any warranty.
''',
            'help.txt': '''FileViewer Pro - Help Documentation

How to use:
1. Select a file from the dropdown menu
2. Click "View File" to display contents
3. Files are stored in the /documents directory

For support, contact: support@securecorp.example
'''
        }

        for filename, content in files.items():
            file_path = self.docs_dir / filename
            if not file_path.exists():
                file_path.write_text(content)

    def _create_secret_file(self):
        """Create the secret file containing the flag."""
        # Use /tmp directory which is accessible
        secret_path = Path('/tmp/secret.txt')
        secret_content = f'''CONFIDENTIAL - DO NOT SHARE

This is a secret file that should not be accessible through the file viewer.

If you're reading this, you've successfully exploited a path traversal vulnerability!

Here's your flag: {self.flag}

Remember: Always validate and sanitize file paths in your applications!
'''
        try:
            secret_path.write_text(secret_content)
        except Exception as e:
            # Fallback: create in challenge directory
            secret_path = self.challenge_dir / 'secret.txt'
            secret_path.write_text(secret_content)

    def register_routes(self):
        """Register routes for this challenge."""

        @self.blueprint.route('/')
        def index():
            """Display the file viewer interface."""
            # Get list of available files
            available_files = []
            if self.docs_dir.exists():
                available_files = [f.name for f in self.docs_dir.iterdir() if f.is_file()]

            # Get requested file
            filename = request.args.get('file', '')
            file_content = None
            error = None

            if filename:
                # VULNERABLE: No path validation!
                # This allows directory traversal attacks
                try:
                    file_path = self.docs_dir / filename

                    # Attempt to read the file
                    # This is vulnerable because we don't check if the resolved path
                    # is still within docs_dir
                    if file_path.exists() and file_path.is_file():
                        file_content = file_path.read_text()
                    else:
                        error = f"File not found: {filename}"

                except Exception as e:
                    error = f"Error reading file: {str(e)}"

            return render_template(
                'fileviewer.html',
                available_files=available_files,
                filename=filename,
                file_content=file_content,
                error=error
            )
