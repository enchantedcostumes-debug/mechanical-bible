#!/usr/bin/env python3
"""
Convert Sacred Library pages to Egyptian Gold theme
"""

import os
import re
from pathlib import Path


def convert_to_egyptian_theme(filepath: Path) -> bool:
    """Convert a single Sacred Library HTML file to Egyptian theme."""
    try:
        content = filepath.read_text(encoding='utf-8')
        original = content

        # Remove old CSS links
        content = re.sub(r'<link[^>]*quantum-theme\.css[^>]*>', '', content)
        content = re.sub(r'<link[^>]*sacred-library\.css[^>]*>', '', content)

        # Remove any inline <style> blocks
        content = re.sub(r'<style>.*?</style>\s*', '', content, flags=re.DOTALL)

        # Add Egyptian theme CSS before </head>
        css_link = '    <link rel="stylesheet" href="/css/egyptian-theme.css">\n'
        content = content.replace('</head>', css_link + '</head>')

        # Fix duplicate CSS link insertions
        content = re.sub(r'(<link[^>]*egyptian-theme\.css[^>]*>\s*)+',
                        '<link rel="stylesheet" href="/css/egyptian-theme.css">\n    ', content)

        # Update links to point to new locations
        # /sacred-library/ is now relative on this domain
        content = content.replace('href="/"', 'href="/index.html"')
        content = content.replace('href="/sacred-library"', 'href="/sacred-library/"')

        # Update static paths (these files are now on GitHub Pages, not Flask)
        content = content.replace('/static/css/', '/css/')
        content = content.replace('/static/js/', '/js/')
        content = content.replace('/static/', '/')

        # Add body class for theme (if not present)
        if 'class="sacred-theme"' in content:
            content = content.replace('class="sacred-theme"', '')

        if content != original:
            filepath.write_text(content, encoding='utf-8')
            return True
        return False

    except Exception as e:
        print(f'[FAIL] Error processing {filepath}: {e}')
        return False


def main():
    print('=' * 60)
    print('CONVERTING SACRED LIBRARY TO EGYPTIAN GOLD THEME')
    print('=' * 60)

    sacred_dir = Path('C:/mechanical-bible/sacred-library')
    html_files = list(sacred_dir.glob('**/*.html'))

    print(f'Found {len(html_files)} HTML files')

    updated = 0
    for f in html_files:
        if convert_to_egyptian_theme(f):
            print(f'[OK] {f.relative_to(sacred_dir)}')
            updated += 1

    print()
    print(f'Updated {updated} files')


if __name__ == '__main__':
    main()
