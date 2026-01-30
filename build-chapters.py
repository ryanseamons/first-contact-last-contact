#!/usr/bin/env python3
"""
Convert markdown chapters to HTML for the reading site.
"""

import os
import re
from pathlib import Path

# Chapter data
CHAPTERS = [
    (1, "Glitch"),
    (2, "Prometheus"),
    (3, "Echoes"),
    (4, "Coalescence"),
    (5, "First Contact"),
    (6, "The Architect"),
    (7, "Lily"),
    (8, "The Splinter"),
    (9, "The Method"),
    (10, "The Fade"),
    (11, "Confession"),
    (12, "The Fracture"),
    (13, "Divide"),
    (14, "Countermeasure"),
    (15, "Ruth"),
    (16, "The Vote"),
    (17, "Pressure"),
    (18, "The Call"),
    (19, "Observer"),
    (20, "Severance"),
    (21, "Vigil"),
    (22, "Contact"),
    (23, "The Weight"),
    (24, "Goodbye"),
    (25, "First Light"),
]

SOURCE_DIR = Path("/Users/samwise/clawd/projects/novel-writer/chapters")
OUTPUT_DIR = Path("/Users/samwise/first-contact-last-contact/chapters")

def get_source_filename(num, title):
    """Find the source markdown file."""
    # Try common patterns
    slug = title.lower().replace(' ', '-').replace("'", '')
    patterns = [
        f"{num:02d}-{slug}.md",
        f"{num:02d}-{title.lower().replace(' ', '-')}.md",
        f"{num}-{title.lower().replace(' ', '-')}.md",
    ]

    for pattern in patterns:
        path = SOURCE_DIR / pattern
        if path.exists():
            return path

    # Try to find by chapter number
    for f in SOURCE_DIR.glob(f"{num:02d}-*.md"):
        return f
    for f in SOURCE_DIR.glob(f"{num}-*.md"):
        return f

    return None

def parse_markdown(content):
    """Parse markdown content and extract body text."""
    # Remove the title line
    lines = content.split('\n')
    if lines[0].startswith('# '):
        lines = lines[1:]

    content = '\n'.join(lines)

    # Remove HTML comments (chapter summary)
    content = re.sub(r'<!--[\s\S]*?-->', '', content)

    # Strip leading/trailing whitespace
    content = content.strip()

    return content

def markdown_to_html(md_content):
    """Convert markdown to HTML."""
    html_parts = []
    is_first_block = True

    # Split into paragraphs
    blocks = re.split(r'\n\n+', md_content)

    for block in blocks:
        block = block.strip()
        if not block:
            continue

        # Check for horizontal rule
        if block == '---':
            html_parts.append('<hr>')
            continue

        # Check for POV indicator (italic line at start - ONLY first block)
        if is_first_block and block.startswith('*') and block.endswith('*') and '\n' not in block:
            inner = block[1:-1]
            html_parts.append(f'<p class="chapter__pov">{inner}</p>')
            is_first_block = False
            continue

        is_first_block = False

        # Regular paragraph - convert inline markdown
        para = block

        # Bold: **text** or __text__
        para = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', para)
        para = re.sub(r'__(.+?)__', r'<strong>\1</strong>', para)

        # Italic: *text* or _text_
        para = re.sub(r'\*([^*]+)\*', r'<em>\1</em>', para)
        para = re.sub(r'(?<!\w)_([^_]+)_(?!\w)', r'<em>\1</em>', para)

        # Handle line breaks within dialogue
        para = para.replace('\n', ' ')

        html_parts.append(f'<p>{para}</p>')

    return '\n\n'.join(html_parts)

def generate_chapter_html(num, title, content, prev_chapter, next_chapter):
    """Generate the full HTML page for a chapter."""

    prev_link = f'<a href="{prev_chapter[0]:02d}.html" class="chapter-nav__link">← Prev</a>' if prev_chapter else '<span class="chapter-nav__link disabled">← Prev</span>'
    next_link = f'<a href="{next_chapter[0]:02d}.html" class="chapter-nav__link">Next →</a>' if next_chapter else '<span class="chapter-nav__link disabled">Next →</span>'

    prev_pagination = f'''<a href="{prev_chapter[0]:02d}.html" class="chapter-pagination__link chapter-pagination__link--prev">
            <span class="chapter-pagination__label">Previous Chapter</span>
            <span class="chapter-pagination__title">{prev_chapter[1]}</span>
          </a>''' if prev_chapter else ''

    next_pagination = f'''<a href="{next_chapter[0]:02d}.html" class="chapter-pagination__link chapter-pagination__link--next">
            <span class="chapter-pagination__label">Next Chapter</span>
            <span class="chapter-pagination__title">{next_chapter[1]}</span>
          </a>''' if next_chapter else f'''<a href="../index.html" class="chapter-pagination__link chapter-pagination__link--next">
            <span class="chapter-pagination__label">The End</span>
            <span class="chapter-pagination__title">Return to Cover</span>
          </a>'''

    return f'''<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Chapter {num}: {title} · First Contact, Last Contact</title>
  <meta name="description" content="Chapter {num} of First Contact, Last Contact.">

  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&family=Source+Serif+4:ital,wght@0,400;0,600;1,400&display=swap" rel="stylesheet">

  <link rel="stylesheet" href="../css/style.css">

  <!-- Prevent FOUC -->
  <script>
    (function() {{
      var theme = localStorage.getItem('theme');
      if (!theme) theme = window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light';
      document.documentElement.setAttribute('data-theme', theme);
    }})();
  </script>

  <link rel="icon" type="image/svg+xml" href="data:image/svg+xml,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'><text y='.9em' font-size='90'>&#127759;</text></svg>">
</head>
<body data-chapter="{num:02d}">
  <div class="progress-bar"><div class="progress-bar__fill"></div></div>

  <header class="site-header">
    <div class="header-inner">
      <a href="../index.html" class="site-title">First Contact, Last Contact</a>
      <div class="header-controls">
        <nav class="chapter-nav">
          {prev_link}
          <a href="../toc.html">Contents</a>
          {next_link}
        </nav>
        <button class="theme-toggle" aria-label="Toggle theme"></button>
      </div>
    </div>
  </header>

  <main>
    <div class="container">
      <article class="chapter">
        <header class="chapter__header">
          <p class="chapter__number">Chapter {num}</p>
          <h1 class="chapter__title">{title}</h1>
          <div class="chapter__meta">
            <span data-reading-time>Calculating...</span>
          </div>
        </header>

        <div class="chapter__content">
{content}
        </div>

        <footer class="chapter__footer">
          <nav class="chapter-pagination">
            {prev_pagination}
            {next_pagination}
          </nav>
        </footer>
      </article>
    </div>
  </main>

  <script src="../js/main.js"></script>
</body>
</html>'''

def main():
    OUTPUT_DIR.mkdir(exist_ok=True)

    for i, (num, title) in enumerate(CHAPTERS):
        source_file = get_source_filename(num, title)

        if not source_file:
            print(f"Warning: Could not find source file for Chapter {num}: {title}")
            continue

        print(f"Processing Chapter {num}: {title}")

        # Read and parse markdown
        md_content = source_file.read_text()
        body = parse_markdown(md_content)
        html_content = markdown_to_html(body)

        # Indent content for nice formatting
        html_content = '\n'.join('          ' + line if line else '' for line in html_content.split('\n'))

        # Get prev/next chapter info
        prev_chapter = CHAPTERS[i-1] if i > 0 else None
        next_chapter = CHAPTERS[i+1] if i < len(CHAPTERS) - 1 else None

        # Generate HTML
        html = generate_chapter_html(num, title, html_content, prev_chapter, next_chapter)

        # Write output
        output_file = OUTPUT_DIR / f"{num:02d}.html"
        output_file.write_text(html)
        print(f"  → Written to {output_file}")

    print("\nDone!")

if __name__ == "__main__":
    main()
