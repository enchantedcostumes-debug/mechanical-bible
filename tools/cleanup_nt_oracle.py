#!/usr/bin/env python3
"""
Cleanup NT Oracle Spans - Mechanical Bible
=============================================
Clears garbage content from <span class="oracle"> in NT chapter HTML files.
The old flat translation text (bracket-wrapped untranslated Greek) was
incorrectly preserved in oracle spans by prepare_nt_html.py.

Copyright (c) 2026 Tammy L Casey. All rights reserved.
"""

import re
from pathlib import Path

BASE_DIR = Path(__file__).parent.parent

NT_BOOKS = [
    'matthew', 'mark', 'luke', 'john', 'acts', 'romans',
    '1_corinthians', '2_corinthians', 'galatians', 'ephesians',
    'philippians', 'colossians', '1_thessalonians', '2_thessalonians',
    '1_timothy', '2_timothy', 'titus', 'philemon',
    'hebrews', 'james', '1_peter', '2_peter',
    '1_john', '2_john', '3_john', 'jude', 'revelation',
]


def main():
    print('=' * 60)
    print('CLEANUP NT ORACLE SPANS')
    print('  Clearing garbage text from <span class="oracle">')
    print('=' * 60)

    total_files = 0
    total_cleaned = 0

    for book in NT_BOOKS:
        book_dir = BASE_DIR / book
        if not book_dir.exists():
            print(f'  SKIP {book}: folder not found')
            continue

        html_files = sorted(book_dir.glob('[0-9]*.html'))
        book_cleaned = 0

        for html_path in html_files:
            with open(html_path, 'r', encoding='utf-8') as f:
                content = f.read()

            # Replace oracle spans that have content with empty oracle spans
            new_content, count = re.subn(
                r'<span class="oracle">(?!<).+?</span>',
                '<span class="oracle"></span>',
                content,
                flags=re.DOTALL
            )

            if count > 0:
                with open(html_path, 'w', encoding='utf-8') as f:
                    f.write(new_content)
                book_cleaned += count

            total_files += 1

        total_cleaned += book_cleaned
        if book_cleaned:
            print(f'  {book}: {book_cleaned} oracle spans cleaned')

    print(f'\n[DONE] Cleaned {total_cleaned:,} oracle spans across {total_files} files')


if __name__ == '__main__':
    main()
