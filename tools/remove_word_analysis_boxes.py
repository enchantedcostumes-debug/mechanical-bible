#!/usr/bin/env python3
"""
Remove redundant Word-by-Word Analysis boxes from chapter HTML files.

The Hebrew words are already shown in the main verse text (clickable).
The gematria values are shown in the modal popup when you click a word.
The "Word-by-Word Analysis" section with boxes is redundant clutter.

Copyright (c) 2026 Tammy L Casey. All rights reserved.
"""

import re
from pathlib import Path


def remove_word_analysis(filepath: Path) -> bool:
    """Remove word-analysis div from a chapter HTML file."""
    try:
        content = filepath.read_text(encoding='utf-8')
        original = content

        # Pattern to match the entire word-analysis div
        # <div class="word-analysis">...all the letter boxes...</div>
        pattern = r'<div class="word-analysis">.*?</div></div>'

        # Replace all occurrences
        content = re.sub(pattern, '', content, flags=re.DOTALL)

        if content != original:
            filepath.write_text(content, encoding='utf-8')
            return True
        return False
    except Exception as e:
        print(f'[FAIL] {filepath}: {e}')
        return False


def main():
    print("=" * 70)
    print("REMOVING REDUNDANT WORD-BY-WORD ANALYSIS BOXES")
    print("=" * 70)

    bible_dir = Path('C:/mechanical-bible')

    # Find all chapter HTML files
    updated = 0
    skipped = 0

    for book_dir in bible_dir.iterdir():
        if not book_dir.is_dir():
            continue
        if book_dir.name.startswith('.') or book_dir.name in ['css', 'js', 'data', 'tools', 'sacred-library']:
            continue

        for chapter_file in book_dir.glob('*.html'):
            if chapter_file.name == 'index.html':
                continue

            if remove_word_analysis(chapter_file):
                updated += 1
                if updated <= 20:
                    print(f'[OK] {chapter_file.relative_to(bible_dir)}')
                elif updated == 21:
                    print('... (showing first 20)')
            else:
                skipped += 1

    print()
    print("=" * 70)
    print(f"DONE: {updated} files updated, {skipped} already clean")
    print("=" * 70)


if __name__ == '__main__':
    main()
