#!/usr/bin/env python3
"""
Update ALL Mechanical Bible HTML files with unified LOGOS header/footer
======================================================================

Adds site-header.js and site-footer.js includes to all pages.
Removes existing inline hero/nav sections that will be replaced by JS.

Copyright (c) 2026 Tammy L Casey. All rights reserved.
"""

import os
import re
from pathlib import Path


def update_html_file(filepath: Path) -> bool:
    """Update a single HTML file with unified header/footer scripts."""
    try:
        content = filepath.read_text(encoding='utf-8')
        original_content = content

        # Skip if already has site-header.js
        if 'site-header.js' in content:
            return False

        # Add site-header.js and site-footer.js before </body>
        scripts = '''    <script src="/js/site-header.js"></script>
    <script src="/js/site-footer.js"></script>
'''
        if '</body>' in content:
            content = content.replace('</body>', scripts + '</body>')

        # Remove existing inline <footer> elements (will be replaced by JS)
        # Pattern: <footer>...</footer> including nested content
        footer_pattern = r'<footer[^>]*>.*?</footer>\s*'
        content = re.sub(footer_pattern, '', content, flags=re.DOTALL)

        # Remove existing hero nav sections (will be replaced by site header)
        # Pattern: <nav>...</nav> inside hero divs
        # We keep the hero div but remove the nav inside it
        hero_nav_pattern = r'(<div class="hero"[^>]*>.*?)(<nav>.*?</nav>)(.*?</div>)'

        def remove_hero_nav(match):
            before = match.group(1)
            after = match.group(3)
            return before + after

        content = re.sub(hero_nav_pattern, remove_hero_nav, content, flags=re.DOTALL)

        # Write if changed
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
    print('UPDATING ALL HTML FILES WITH UNIFIED LOGOS HEADER/FOOTER')
    print('=' * 70)

    bible_dir = Path('C:/mechanical-bible')

    # Find ALL HTML files
    html_files = list(bible_dir.glob('**/*.html'))

    print(f'Found {len(html_files)} HTML files to process')
    print()

    updated = 0
    skipped = 0

    for filepath in html_files:
        result = update_html_file(filepath)
        if result:
            updated += 1
            if updated <= 30:
                print(f'[OK] Updated: {filepath.relative_to(bible_dir)}')
            elif updated == 31:
                print('... (showing first 30 only)')
        else:
            skipped += 1

    print()
    print('=' * 70)
    print(f'SUMMARY: {updated} updated, {skipped} skipped (already had scripts)')
    print('=' * 70)


if __name__ == '__main__':
    main()
