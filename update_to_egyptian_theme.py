#!/usr/bin/env python3
"""
Update ALL Mechanical Bible HTML files to Egyptian Gold Theme
=============================================================

Replaces inline styles with external CSS link to egyptian-theme.css
Preserves all content, just changes the styling approach.

Copyright (c) 2026 Tammy L Casey. All rights reserved.
"""

import os
import re
from pathlib import Path


def update_html_file(filepath: Path) -> bool:
    """Update a single HTML file to use Egyptian theme."""
    try:
        content = filepath.read_text(encoding='utf-8')
        original_content = content

        # Skip if already using egyptian-theme.css
        if 'egyptian-theme.css' in content:
            return False

        # Skip root index.html (it has its own complete styling)
        if filepath.name == 'index.html' and filepath.parent == Path('.'):
            return False

        # 1. Remove inline <style> block entirely
        # Pattern: <style>...</style>
        style_pattern = r'<style>.*?</style>\s*'
        content = re.sub(style_pattern, '', content, flags=re.DOTALL)

        # 2. Add CSS links before </head>
        css_links = '''    <link rel="stylesheet" href="/css/egyptian-theme.css">
    <link rel="stylesheet" href="/css/word-modal.css">
'''
        content = content.replace('</head>', css_links + '</head>')

        # 3. Fix any double CSS link insertions
        content = re.sub(r'(<link rel="stylesheet" href="/css/egyptian-theme.css">\s*)+',
                        '<link rel="stylesheet" href="/css/egyptian-theme.css">\n    ', content)

        # 4. Update body styling if it has old class
        # The old theme used body { background: #f8f6f3; color: #2c2416; }
        # We don't need to do anything because CSS handles it

        # 5. Write if changed
        if content != original_content:
            filepath.write_text(content, encoding='utf-8')
            return True
        return False

    except Exception as e:
        print(f'[FAIL] Error processing {filepath}: {e}')
        return False


def main():
    """Main execution."""
    print('=' * 70)
    print('UPDATING ALL HTML FILES TO EGYPTIAN GOLD THEME')
    print('=' * 70)

    bible_dir = Path('.')

    # Find ALL HTML files
    html_files = list(bible_dir.glob('**/*.html'))

    # Exclude root index.html (it has complete styling)
    html_files = [f for f in html_files if not (f.name == 'index.html' and f.parent == Path('.'))]

    print(f'Found {len(html_files)} HTML files to process')
    print()

    updated = 0
    skipped = 0
    errors = 0

    for filepath in html_files:
        result = update_html_file(filepath)
        if result:
            updated += 1
            if updated <= 20:
                print(f'[OK] Updated: {filepath}')
            elif updated == 21:
                print('... (showing first 20 only)')
        else:
            skipped += 1

    print()
    print('=' * 70)
    print(f'SUMMARY: {updated} updated, {skipped} skipped (already themed)')
    print('=' * 70)


if __name__ == '__main__':
    main()
