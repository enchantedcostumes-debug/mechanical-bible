# CLAUDE.md - Mechanical Bible Project Guidelines

## CRITICAL: Repository Location
- **The repo is at `C:\mechanical-bible`** — NOWHERE ELSE
- NEVER clone, copy, or create another instance of this repo
- ALL work happens in `C:\mechanical-bible`

## CRITICAL: File Paths
- ONE CSS directory: `C:\mechanical-bible\css\`
- ONE JS directory: `C:\mechanical-bible\js\`
- All book chapter files are ONE level deep (e.g., `genesis/1.html`)
- Chapter HTML files use `../css/` and `../js/` (relative, one level up)
- Root HTML files use `css/` and `js/` (relative, same level)
- NEVER use absolute paths like `/css/` — they break local viewing
- NEVER nest CSS folders or create alternative CSS locations

## CRITICAL: Test Before Committing
- Open the HTML files in a browser FROM `C:\mechanical-bible` and verify:
  - Styles load (gold Egyptian theme visible)
  - Content renders correctly
  - No blank white pages
- Do NOT push to git until the user has reviewed locally

## HTML Structure
- Every chapter HTML file links to `../css/egyptian-theme.css` and `../css/word-modal.css`
- Verse structure: `<div class="verse">` containing `verse-ref`, `original-text`, `translation`, optional `footnotes` and `cross-refs`
- Keep div nesting balanced — count opens vs closes
- Translation div contains three layers: `.rmt` (visible), `.mechanical` (hidden), `.jps` (hidden)

## Translation Layers
- **RMT**: Revised Mechanical Translation (Jeff Benner style, natural English, Hebrew names preserved)
- **Mechanical**: Word-for-word with prefix notation (e.g., `in~SUMMIT SHAPE(V) POWER~s`)
- **JPS**: Original Jewish Publication Society text preserved as reference layer
- Source methodology: Jeff Benner, Ancient Hebrew Lexicon of the Bible (AHLB)

## Key Data Files
- `words.json` — 58,000+ Hebrew/Greek word entries with definitions, gematria, pictographs
- `data/ahlb_complete.json` — Parsed AHLB lexicon
- `data/ahlb_by_strongs.json` — AHLB indexed by Strong's numbers
- AHLB source text: `C:\Users\Tammy Casey\Documents\AI PROJECTS\1 Website\EXTRACTED_FILES\raw_data\docs\ahlb.txt`
- AHLB PDF: `C:\Users\Tammy Casey\Downloads\PDFs\ahlb.pdf`

## Don't Be Stupid
- Read existing files before modifying them
- Don't create new directories or files unless absolutely necessary
- Don't over-engineer — keep it simple
- If something seems wrong, CHECK before "fixing" it
- Ask if unsure — don't guess and break things
