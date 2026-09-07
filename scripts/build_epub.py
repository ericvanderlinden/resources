"""
build_heinsius_epub.py
======================
Builds an ePub3 for the Briefwisseling Heinsius from the CSV + ocr_v2 text.

Structure mirrors the PDF version:
  - One HTML file per page  (filebasename.xhtml)
  - NCX / nav ToC with same hierarchy as the PDF bookmarks:
      Voorwerk
          I, II, … XXXIV
      Inleiding          ← first page of Inleiding
      Briefwisseling     ← first page of Briefwisseling
          1  van Albemarle …
          2  van Marlborough …
          …
      Lijst van gebruikte afkortingen
      Overzicht van de vindplaatsen …
      …

Usage
-----
    pip install ebooklib
    python build_heinsius_epub.py

Output: heinsius_01_GS158.epub
"""

import os,re
import uuid
import pandas as pd
from pathlib import Path
from ebooklib import epub

# ── Config ────────────────────────────────────────────────────────────────────

# CSV_FILE   = "heinsius_01_GS158_by_page.csv"
# OUTPUT     = "heinsius_01_GS158.epub"
BOOK_TITLE = "De briefwisseling van Anthonie Heinsius, 1702–1720. Deel I"
BOOK_LANG  = "nl"
BOOK_ID    = str(uuid.uuid4())
# ── Configuration ────────────────────────────────────────────────────────────

workspace = os.getenv("GITHUB_WORKSPACE", "../")
GROUP = "retro"
SERIES = "heinsius"
BOOK = "heinsius_01_GS158"

# CSV_FILE   = "heinsius_01_GS158_by_page.csv"
CSV_FILE = os.path.join(workspace, "{}/{}/{}/dataset/csv/{}_by_page.csv".format(GROUP,SERIES,BOOK,BOOK))
OUTPUT_PRODUCTS = os.path.join(workspace, "{}/{}/{}/products".format(GROUP,SERIES,BOOK))
OUTPUT_EPUB = os.path.join(OUTPUT_PRODUCTS,"{}.epub".format(BOOK))
# CACHE_DIR  = os.path.join(workspace, "pdf_cache")  # created pdf pages are cached here
# IMAGE_DIR = os.path.join(workspace, "{}/{}/{}/tiff".format(GROUP,SERIES,BOOK))

# ── CSS ───────────────────────────────────────────────────────────────────────

CSS = """\
body {
    font-family: Georgia, serif;
    font-size: 1em;
    line-height: 1.6;
    margin: 1.5em 2em;
    color: #111;
}
h1 { font-size: 1.4em; margin-top: 1.5em; border-bottom: 1px solid #ccc; }
h2 { font-size: 1.15em; margin-top: 1.2em; }
p  { margin: 0.5em 0; text-align: justify; }
.page-number {
    font-size: 0.75em;
    color: #999;
    text-align: right;
    margin-bottom: 0.8em;
    border-bottom: 1px solid #eee;
}
.letter-block { margin-top: 1.5em; }
"""

# ── Helpers ───────────────────────────────────────────────────────────────────

def ocr_to_html(ocr: str) -> str:
    """Convert ocr_v2 (text with <br />) to clean paragraphs."""
    if not isinstance(ocr, str):
        return "<p><em>[geen tekst]</em></p>"
    # Normalise line breaks
    text = ocr.replace("<br />", "\n").replace("<br/>", "\n").replace("<br>", "\n")
    # Split into paragraphs on blank lines
    paragraphs = re.split(r"\n{2,}", text)
    parts = []
    for para in paragraphs:
        para = para.strip()
        if not para:
            continue
        # Convert remaining single newlines to spaces
        para = para.replace("\n", " ")
        # Escape any stray HTML characters (except we already handled <br>)
        para = para.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
        parts.append(f"<p>{para}</p>")
    return "\n".join(parts)


def make_xhtml(title: str, page_label: str, body_html: str) -> str:
    return f"""<?xml version="1.0" encoding="utf-8"?>
<!DOCTYPE html>
<html xmlns="http://www.w3.org/1999/xhtml" xml:lang="nl" lang="nl">
<head>
  <meta charset="utf-8"/>
  <title>{title}</title>
  <link rel="stylesheet" type="text/css" href="../styles/main.css"/>
</head>
<body>
  <div class="page-number">{page_label}</div>
  {body_html}
</body>
</html>"""


# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    print("Loading CSV …")
    df = pd.read_csv(CSV_FILE)
    print(f"  {len(df)} rows")

    book = epub.EpubBook()
    book.set_identifier(BOOK_ID)
    book.set_title(BOOK_TITLE)
    book.set_language(BOOK_LANG)
    book.add_author("A.J. Veenendaal jr.")

    # Add CSS
    css_item = epub.EpubItem(
        uid="main-css",
        file_name="styles/main.css",
        media_type="text/css",
        content=CSS.encode("utf-8"),
    )
    book.add_item(css_item)

    # ── Build one EpubHtml per row ────────────────────────────────────────────
    epub_pages: list[epub.EpubHtml] = []   # in document order
    uid_map: dict[str, epub.EpubHtml] = {} # filebasename → EpubHtml

    for _, row in df.iterrows():
        basename  = row["filebasename"]
        file_num  = str(row["file_number"])
        matter    = row["matter_type"]
        h0        = str(row["level_0_heading"]) if pd.notna(row["level_0_heading"]) else ""
        ocr       = row["ocr_v2"]

        # Page label for display
        page_label = f"p. {file_num}"

        # Chapter title (used in spine / fallback)
        if matter == "FrontMatter":
            chap_title = file_num
        elif matter == "BodyMatter":
            chap_title = f"p. {file_num}"
        else:
            chap_title = h0 or file_num

        body_html = ocr_to_html(ocr)
        xhtml     = make_xhtml(chap_title, page_label, body_html)

        item = epub.EpubHtml(
            uid=basename,
            file_name=f"text/{basename}.xhtml",
            title=chap_title,
            lang=BOOK_LANG,
            content=xhtml.encode("utf-8"),
        )
        item.add_item(css_item)
        book.add_item(item)
        epub_pages.append(item)
        uid_map[basename] = item

    # ── Build NCX / nav ToC ───────────────────────────────────────────────────
    #
    # Same hierarchy as the PDF:
    #   Voorwerk  (top)
    #       I, II … XXXIV  (children)
    #   Inleiding  (top, from FrontMatter with heading)
    #   Briefwisseling  (top, BodyMatter)
    #       1 van Albemarle …  (children – first page per letter)
    #   BackMatter sections  (top)

    toc = []

    # ── Voorwerk ──────────────────────────────────────────────────────────────
    front_rows = df[df["matter_type"] == "FrontMatter"]
    if len(front_rows):
        first_front_item = uid_map[front_rows.iloc[0]["filebasename"]]
        front_children = []
        for _, row in front_rows.iterrows():
            item  = uid_map[row["filebasename"]]
            fn    = str(row["file_number"])
            h0    = str(row["level_0_heading"]) if pd.notna(row["level_0_heading"]) else ""
            label = h0 if h0 and h0 not in ("nan", "no_value") else fn
            label = re.sub(r"<[^>]+>", " ", label).strip()[:80]
            label = f"{fn}  {label}" if label != fn else fn
            front_children.append(epub.Link(item.file_name, label, item.id + "_toc"))
        toc.append((
            epub.Section("Voorwerk", href=first_front_item.file_name),
            front_children,
        ))

    # ── Inleiding (FrontMatter rows with heading set) ─────────────────────────
    prev_h0 = None
    for _, row in front_rows.iterrows():
        h0 = str(row["level_0_heading"]) if pd.notna(row["level_0_heading"]) else ""
        if h0 and h0 not in ("nan", "no_value") and h0 != prev_h0:
            item = uid_map[row["filebasename"]]
            toc.append(epub.Link(item.file_name, h0, item.id + "_inl"))
            prev_h0 = h0

    # ── BodyMatter sections + letter children ─────────────────────────────────

    # Build letter → first-page map (same logic as PDF script)
    letter_entries: list[tuple[int, str, str]] = []  # (num, label, filebasename)
    for _, row in df[df["matter_type"] == "BodyMatter"].iterrows():
        if pd.isna(row["item_number"]):
            continue
        nums   = [s.strip() for s in str(row["item_number"]).split(";")]
        titles = [s.strip() for s in str(row["title"]).split(";")] if pd.notna(row["title"]) else []
        for j, num in enumerate(nums):
            try:
                n = int(num)
            except ValueError:
                continue
            t = titles[j] if j < len(titles) else ""
            letter_entries.append((n, t, row["filebasename"]))

    seen: set[int] = set()
    unique_letters: list[tuple[int, str, str]] = []
    for n, t, bn in sorted(letter_entries, key=lambda x: x[0]):
        if n not in seen:
            seen.add(n)
            unique_letters.append((n, t, bn))

    body_rows = df[df["matter_type"] == "BodyMatter"]
    prev_h0 = None
    for _, row in body_rows.iterrows():
        h0 = str(row["level_0_heading"]) if pd.notna(row["level_0_heading"]) else ""
        if h0 and h0 != prev_h0:
            item = uid_map[row["filebasename"]]
            if h0 == "Briefwisseling":
                children = []
                for n, t, bn in unique_letters:
                    label = f"{n}  {t}" if t else str(n)
                    child_item = uid_map[bn]
                    children.append(
                        epub.Link(child_item.file_name, label, f"letter_{n}")
                    )
                toc.append((
                    epub.Section("Briefwisseling", href=item.file_name),
                    children,
                ))
            else:
                toc.append(epub.Link(item.file_name, h0, item.id + "_body"))
            prev_h0 = h0

    # ── BackMatter sections ───────────────────────────────────────────────────
    back_rows = df[df["matter_type"] == "BackMatter"]
    prev_h0 = None
    for _, row in back_rows.iterrows():
        h0 = str(row["level_0_heading"]) if pd.notna(row["level_0_heading"]) else ""
        if h0 and h0 not in ("nan", "no_value") and h0 != prev_h0:
            item = uid_map[row["filebasename"]]
            toc.append(epub.Link(item.file_name, h0, item.id + "_back"))
            prev_h0 = h0

    book.toc = toc

    # ── Spine (reading order = document order) ────────────────────────────────
    book.spine = ["nav"] + epub_pages

    # ── Required ePub navigation items ───────────────────────────────────────
    book.add_item(epub.EpubNcx())
    book.add_item(epub.EpubNav())

    # ── Write ─────────────────────────────────────────────────────────────────
    print(f"Writing {OUTPUT_EPUB} …")
    epub.write_epub(OUTPUT_EPUB, book)
    import os
    size_mb = os.path.getsize(OUTPUT_EPUB) / 1_000_000
    print(f"\n✓ Done!  {OUTPUT_EPUB}  ({size_mb:.1f} MB)")
    print(f"  {len(epub_pages)} pages  |  {len(unique_letters)} letters in ToC")


if __name__ == "__main__":
    main()
