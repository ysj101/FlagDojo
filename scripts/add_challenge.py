#!/usr/bin/env python3
"""
Challenge Generator Script
Creates a new challenge template with all necessary files.

Usage:
    python scripts/add_challenge.py --slug my-challenge --title "My Challenge" --category XSS --difficulty easy
"""

import argparse
import sys
from pathlib import Path


CHALLENGE_TEMPLATE = '''"""
{title} Challenge
INTENTIONALLY VULNERABLE - For educational purposes only
"""
from flask import request, render_template, redirect, url_for, flash
from app.base_challenge import BaseChallenge


class {class_name}(BaseChallenge):
    """
    {title} challenge - {description}
    """

    # Challenge metadata
    slug = '{slug}'
    title = '{title}'
    category = '{category}'
    difficulty = '{difficulty}'
    points = {points}
    description = \'\'\'
    {description}

    **Objective**: [Describe the goal of this challenge]
    \'\'\'
    flag = 'FLAG{{{flag_placeholder}}}'
    hints = [
        'Hint 1: [Your first hint]',
        'Hint 2: [Your second hint]',
        'Hint 3: [Your third hint]',
    ]
    order = {order}

    def register_routes(self):
        """Register routes for this challenge."""

        @self.blueprint.route('/')
        def index():
            """
            Main challenge page.
            TODO: Implement your challenge logic here.
            """
            return render_template('index.html')

        # Add more routes as needed

    def setup_database(self, db):
        """
        Optional: Setup challenge-specific database tables.

        Example:
            class MyTable(db.Model):
                __tablename__ = '{slug}_data'
                id = db.Column(db.Integer, primary_key=True)
                content = db.Column(db.Text)

            self.MyTable = MyTable
        """
        pass
'''

HTML_TEMPLATE = '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title} - FlagDojo</title>
    <script src="https://cdn.tailwindcss.com"></script>
</head>
<body class="bg-gray-900 text-white min-h-screen">
    <div class="container mx-auto px-4 py-8 max-w-4xl">
        <!-- Header -->
        <div class="mb-8">
            <a href="/" class="text-blue-400 hover:text-blue-300 mb-4 inline-block">&larr; Back to Challenges</a>
            <h1 class="text-4xl font-bold mb-2">{title}</h1>
            <p class="text-gray-400">{description}</p>
        </div>

        <!-- Flash Messages -->
        {{% with messages = get_flashed_messages(with_categories=true) %}}
            {{% if messages %}}
                {{% for category, message in messages %}}
                    <div class="mb-4 p-4 rounded-lg {{% if category == 'danger' %}}bg-red-500/20 border border-red-500{{% elif category == 'success' %}}bg-green-500/20 border border-green-500{{% else %}}bg-blue-500/20 border border-blue-500{{% endif %}}">
                        {{{{ message }}}}
                    </div>
                {{% endfor %}}
            {{% endif %}}
        {{% endwith %}}

        <!-- Challenge Content -->
        <div class="bg-gray-800 rounded-lg p-6 border border-gray-700">
            <h2 class="text-2xl font-bold mb-4">Challenge Area</h2>
            <p class="text-gray-300">
                TODO: Implement your challenge UI here.
            </p>
        </div>

        <!-- Challenge Hint -->
        <div class="mt-8 bg-yellow-500/10 border border-yellow-500/50 rounded-lg p-6">
            <h3 class="text-xl font-bold mb-2 text-yellow-400">💡 Challenge Objective</h3>
            <p class="text-gray-300 mb-4">
                [Describe what the user needs to do to solve this challenge]
            </p>
            <details>
                <summary class="cursor-pointer text-blue-400 hover:text-blue-300">Click for hints</summary>
                <ul class="mt-2 space-y-1 text-sm text-gray-400 list-disc list-inside">
                    <li>Hint 1</li>
                    <li>Hint 2</li>
                    <li>Hint 3</li>
                </ul>
            </details>
        </div>
    </div>
</body>
</html>
'''

README_TEMPLATE = '''# {title}

**Category**: {category}
**Difficulty**: {difficulty}
**Points**: {points}

## Description

{description}

## Learning Objectives

- [Learning objective 1]
- [Learning objective 2]
- [Learning objective 3]

## Solution

<details>
<summary>Click to reveal solution</summary>

### Exploitation Steps

1. Step 1
2. Step 2
3. Step 3

### Flag

`FLAG{{{flag_placeholder}}}`

### Remediation

To fix this vulnerability:
- Fix 1
- Fix 2
- Fix 3

</details>

## References

- [OWASP Resource](https://owasp.org/)
- [Additional Resource](https://example.com/)
'''


def to_class_name(slug):
    """Convert slug to PascalCase class name."""
    parts = slug.split('-')
    return ''.join(word.capitalize() for word in parts) + 'Challenge'


def to_flag_placeholder(slug):
    """Convert slug to flag placeholder."""
    return slug.replace('-', '_')


def get_points(difficulty):
    """Get default points based on difficulty."""
    points_map = {
        'easy': 100,
        'medium': 200,
        'hard': 300
    }
    return points_map.get(difficulty.lower(), 100)


def create_challenge(slug, title, category, difficulty, description, order):
    """Create a new challenge from template."""

    # Validate slug
    if not slug or not slug.replace('-', '').replace('_', '').isalnum():
        print("❌ Error: Slug must contain only letters, numbers, hyphens, and underscores")
        return False

    # Get project root
    script_dir = Path(__file__).parent
    project_root = script_dir.parent
    challenges_dir = project_root / 'challenges'

    # Create challenge directory
    challenge_dir = challenges_dir / slug

    if challenge_dir.exists():
        print(f"❌ Error: Challenge '{slug}' already exists at {challenge_dir}")
        return False

    try:
        # Create directories
        challenge_dir.mkdir(parents=True)
        templates_dir = challenge_dir / 'templates'
        templates_dir.mkdir()

        print(f"📁 Created directory: {challenge_dir}")

        # Generate files from templates
        class_name = to_class_name(slug)
        flag_placeholder = to_flag_placeholder(slug)
        points = get_points(difficulty)

        # Create challenge.py
        challenge_py = challenge_dir / 'challenge.py'
        challenge_py.write_text(CHALLENGE_TEMPLATE.format(
            slug=slug,
            title=title,
            category=category,
            difficulty=difficulty,
            points=points,
            description=description,
            class_name=class_name,
            flag_placeholder=flag_placeholder,
            order=order
        ))
        print(f"✅ Created: {challenge_py}")

        # Create index.html
        index_html = templates_dir / 'index.html'
        index_html.write_text(HTML_TEMPLATE.format(
            title=title,
            description=description
        ))
        print(f"✅ Created: {index_html}")

        # Create README.md
        readme_md = challenge_dir / 'README.md'
        readme_md.write_text(README_TEMPLATE.format(
            title=title,
            category=category,
            difficulty=difficulty,
            points=points,
            description=description,
            flag_placeholder=flag_placeholder
        ))
        print(f"✅ Created: {readme_md}")

        print(f"\n🎉 Challenge '{slug}' created successfully!")
        print(f"\n📝 Next steps:")
        print(f"1. Edit {challenge_py} to implement your challenge logic")
        print(f"2. Customize {index_html} to create the challenge UI")
        print(f"3. Update {readme_md} with solution details")
        print(f"4. Restart the Flask application to load the new challenge")
        print(f"\n🚀 The challenge will be automatically discovered and loaded!")

        return True

    except Exception as e:
        print(f"❌ Error creating challenge: {e}")
        # Clean up on error
        if challenge_dir.exists():
            import shutil
            shutil.rmtree(challenge_dir)
        return False


def main():
    parser = argparse.ArgumentParser(
        description='Generate a new FlagDojo challenge from template',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
Examples:
  python scripts/add_challenge.py --slug xss-dom --title "DOM XSS" --category XSS --difficulty medium
  python scripts/add_challenge.py --slug xxe-basic --title "XXE Attack" --category XXE --difficulty hard --description "XML External Entity vulnerability"
        '''
    )

    parser.add_argument('--slug', required=True,
                       help='Challenge slug (URL-friendly identifier, e.g., "xss-dom")')
    parser.add_argument('--title', required=True,
                       help='Challenge title (e.g., "DOM-based XSS")')
    parser.add_argument('--category', required=True,
                       help='Challenge category (e.g., XSS, SQLi, CSRF)')
    parser.add_argument('--difficulty', required=True,
                       choices=['easy', 'medium', 'hard'],
                       help='Challenge difficulty level')
    parser.add_argument('--description', default='A new security challenge.',
                       help='Brief description of the challenge')
    parser.add_argument('--order', type=int, default=99,
                       help='Display order (default: 99)')

    args = parser.parse_args()

    # Create the challenge
    success = create_challenge(
        slug=args.slug,
        title=args.title,
        category=args.category,
        difficulty=args.difficulty,
        description=args.description,
        order=args.order
    )

    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()
